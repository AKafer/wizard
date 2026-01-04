import logging

import sqlalchemy
from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends, HTTPException
from fastapi_filter import FilterDepends
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database.models.certificates import Certificates, Status
from database.models.transactions import Transactions
from dependencies import get_db_session, get_kafka_producer
from main_schemas import ResponseErrorBody
from settings import RATE_LIMITER_SECONDS, RATE_LIMITER_TIMES
from web.certificates.filters import CertFilter
from web.certificates.schemas import (
    Certificate,
    CertificateAmount,
    CertificateCreate,
    CertificateUpdate,
)
from web.certificates.services import (
    ErrorSaveToDatabase,
    hide_cert_sentitive_info,
    send_certificate_charged_event,
    set_actual_status,
    update_cert_in_db,
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
    '/charge/{cert_id}',
    status_code=status.HTTP_200_OK,
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
async def charge_certificate(
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

    actual_amount = round(max(0, cert.amount - charge_sum), 2)
    cert.amount = actual_amount
    set_actual_status(cert)

    transaction = Transactions(cert_id=cert.id, amount=-charge_sum)
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)

    try:
        await send_certificate_charged_event(
            kafka_producer,
            cert_id=cert_id,
            tran_id=transaction.id,
            cert_code=cert.code,
            charge_sum=charge_sum,
            new_amount=cert.amount,
            status=str(cert.status),
            phone=cert.phone,
        )
        logger.info(
            'CERTIFICATE_CHARGED event sent for cert_id %s: charged %s, new amount %s',
            cert_id,
            charge_sum,
            cert.amount,
        )
    except Exception as e:
        logger.error(
            'Failed to send CERTIFICATE_CHARGED event for cert_id %s: %s',
            cert_id,
            e,
        )

    return cert
