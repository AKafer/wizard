import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from fastapi_filter import FilterDepends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from core.helpers import is_cert_expired
from database.models.certificates import Certificates, Type
from dependencies import get_db_session
from main_schemas import ResponseErrorBody
from web.certificates.filters import CertFilter
from web.certificates.schemas import Certificate, CertificateCreate, CertificateAmount, CertificateUpdate
from web.certificates.services import update_cert_in_db, ErrorSaveToDatabase, set_actual_status
from web.users.users import current_superuser, current_user, fastapi_users

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
    certs =  result.scalars().all()
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

    if not user or not getattr(user, "is_superuser", False):
        cert.user.phone_number = "*********" + (cert.user.phone_number or "")[-3:]
        cert.user.name = cert.user.name[0] + "******"
        cert.user.last_name = cert.user.last_name[0] + "******"
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
        db_cert = await update_cert_in_db(
            cert, **update_dict
        )
        set_actual_status(db_cert)
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
):
    query = select(Certificates).filter(Certificates.id == cert_id)
    cert = await db_session.scalar(query)
    if cert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Certificate with id {cert_id} not found',
        )

    if cert.status != Type.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Only ACTIVE certificates can be charged. Current status: {cert.status}',
        )

    actual_amount = max(0, cert.amount - charge_sum)
    cert.amount = actual_amount
    set_actual_status(cert)
    await db_session.commit()
    return cert
