import logging
from datetime import timedelta

import sqlalchemy
from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends, HTTPException
from fastapi_filter import FilterDepends
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

import settings
from database.models.certificates import Certificates, Status
from database.models.transactions import StatusTran, Transactions
from dependencies import get_db_session, get_kafka_producer
from main_schemas import ResponseErrorBody
from settings import RATE_LIMITER_SECONDS, RATE_LIMITER_TIMES
from web.certificates.filters import CertFilter
from web.certificates.schemas import (
    Certificate,
    CertificateAmount,
    CertificateCreate,
    CertificateUpdate, TelegramMsgBody,
)
from web.certificates.services import (
    ErrorSaveToDatabase,
    generate_secure_code,
    hide_cert_sentitive_info,
    send_certificate_charged_event,
    set_actual_status,
    update_cert_in_db, send_telegram_msg_event, hide_phone, get_telegram_text,
)
from web.users.users import current_superuser, fastapi_users

logger = logging.getLogger('wizard')


router = APIRouter(prefix='/certificates', tags=['certificates'])


current_user_optional = fastapi_users.current_user(optional=True)


@router.get(
    '/',
    response_model=list[Certificate],
    dependencies=[Depends(current_superuser)],
)
async def get_all_certificates(
    cert_filter: CertFilter = FilterDepends(CertFilter),
    db_session: AsyncSession = Depends(get_db_session),
):
    query = select(Certificates)
    query = cert_filter.filter(query)
    result = await db_session.execute(query)
    certs = result.scalars().all()
    for cert in certs:
        set_actual_status(cert)
    await db_session.commit()
    return certs


@router.get(
    '/{cert_id}',
    response_model=CertificateAmount,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'model': ResponseErrorBody,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': ResponseErrorBody,
        },
    },
    dependencies=[
        Depends(
            RateLimiter(times=RATE_LIMITER_TIMES, seconds=RATE_LIMITER_SECONDS)
        )
    ],
)
async def get_cert_by_id(
    cert_id: str,
    user=Depends(current_user_optional),
    db_session: AsyncSession = Depends(get_db_session),
):
    query = select(Certificates).filter(Certificates.id == cert_id)
    cert = await db_session.scalar(query)
    if cert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Certificate with id {cert_id} not found',
        )

    set_actual_status(cert)
    await db_session.commit()

    if not user or not getattr(user, 'is_superuser', False):
        hide_cert_sentitive_info(cert)

    return cert


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=Certificate,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'model': ResponseErrorBody,
        },
    },
    dependencies=[Depends(current_superuser)],
)
async def create_certificate(
    input_data: CertificateCreate,
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        db_certificate = Certificates(**input_data.dict())
        db_certificate.amount = db_certificate.nominal
        db_session.add(db_certificate)
        await db_session.commit()
        await db_session.refresh(db_certificate)
    except sqlalchemy.exc.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Integrity error: {e.orig}',
        )
    return db_certificate


@router.patch(
    '/{cert_id}',
    response_model=Certificate,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'model': ResponseErrorBody,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': ResponseErrorBody,
        },
    },
    dependencies=[Depends(current_superuser)],
)
async def update_certificate(
    cert_id: str,
    update_data: CertificateUpdate,
    db_session: AsyncSession = Depends(get_db_session),
):
    update_dict = update_data.dict(exclude_none=True)
    query = select(Certificates).filter(Certificates.id == cert_id)
    cert = await db_session.scalar(query)
    if cert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Certificate with id {cert_id} not found',
        )
    try:
        db_cert = await update_cert_in_db(cert, **update_dict)
        set_actual_status(db_cert)

        if update_data.amount is not None:
            if update_data.amount > cert.nominal:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Amount cannot be greater than nominal value',
                )

            if update_data.amount - cert.amount != 0:
                transaction = Transactions(
                    cert_id=db_cert.id, amount=update_data.amount - cert.amount
                )
                db_session.add(transaction)

        await db_session.commit()
        await db_session.refresh(db_cert)
    except ErrorSaveToDatabase as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Error updating certificate: {e}',
        )
    return db_cert


@router.post(
    '/send_confirm_code/{cert_id}',
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'model': ResponseErrorBody,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': ResponseErrorBody,
        },
    },
    dependencies=[Depends(current_superuser)],
)
async def send_confirm_code(
    cert_id: str,
    charge_sum: float,
    db_session: AsyncSession = Depends(get_db_session),
    kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer),
):
    query = select(Certificates).filter(Certificates.id == cert_id)
    cert = await db_session.scalar(query)

    if cert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Certificate with id {cert_id} not found',
        )

    if cert.status != Status.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Only ACTIVE certificates can be charged. Current status: {cert.status}',
        )

    if charge_sum < 0 or charge_sum > cert.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Charge sum cannot be negative or greater than total amount',
        )

    confirm_code = generate_secure_code()

    tran = Transactions(
        cert_id=cert.id,
        amount=-charge_sum,
        confirm_code=confirm_code,
    )
    db_session.add(tran)
    await db_session.flush()

    cert.actual_tran_id = tran.id

    await db_session.commit()
    await db_session.refresh(cert)
    await db_session.refresh(tran)

    try:
        await send_certificate_charged_event(
            kafka_producer,
            cert_id=cert_id,
            tran_id=tran.id,
            cert_code=cert.code,
            charge_sum=charge_sum,
            confirm_code=confirm_code,
            phone=cert.phone,
        )
        logger.info(
            'Confirm code sent successfully for certificate %s', cert_id
        )
    except Exception as e:
        logger.error(
            'Failed to send confirmation code for certificate %s, %s',
            cert_id,
            e,
        )

    return JSONResponse(content={'result': 'ok'})


@router.post(
    '/charge/{cert_id}',
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'model': ResponseErrorBody,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': ResponseErrorBody,
        },
    },
    dependencies=[Depends(current_superuser)],
)
async def charge_certificate(
    cert_id: str,
    confirm_code: str,
    db_session: AsyncSession = Depends(get_db_session),
):
    query = select(Certificates).filter(Certificates.id == cert_id)
    cert = await db_session.scalar(query)

    if cert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Certificate with id {cert_id} not found',
        )

    if cert.status != Status.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Only ACTIVE certificates can be charged. Current status: {cert.status}',
        )

    if not cert.actual_tran_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Certificate with id {cert_id} has no active transaction',
        )

    query = select(Transactions).filter(Transactions.id == cert.actual_tran_id)
    tran = await db_session.scalar(query)

    if tran is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Not found actual transaction id for cert: {cert_id}',
        )

    if tran.status in [StatusTran.DONE, StatusTran.CANCELLED]:
        raise HTTPException(
            400, detail='Transaction already done or cancelled'
        )

    if confirm_code != tran.confirm_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Confirm code does not match transaction confirmation code',
        )

    cert.amount = cert.amount + tran.amount
    set_actual_status(cert)
    tran.status = StatusTran.DONE

    await db_session.commit()
    await db_session.refresh(cert)

    return JSONResponse(content={'result': 'ok'})


@router.post(
    '/send_telegram_msg/{cert_id}',
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'model': ResponseErrorBody,
        },
        status.HTTP_404_NOT_FOUND: {
            'model': ResponseErrorBody,
        },
    },
    dependencies=[Depends(current_superuser)],
)
async def send_telegram_msg(
    cert_id: str,
    input_data: TelegramMsgBody,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer),
):
    query = select(Certificates).filter(Certificates.id == cert_id)
    cert = await db_session.scalar(query)

    if cert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Certificate with id {cert_id} not found',
        )

    if cert.status != Status.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Certificate with id {cert_id} is not active',
        )

    text = get_telegram_text(cert, request)
    image_url = (
        input_data.image_url
        or settings.TELEGRAM_DEFAULT_IMAGE_URL
    )

    try:
        await send_telegram_msg_event(
            kafka_producer, chat_id=input_data.chat_id, image_url=image_url, text=text
        )
    except Exception as e:
        logger.exception("send_telegram_msg_event failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return JSONResponse(content={'result': 'ok'})
