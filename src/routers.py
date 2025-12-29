from fastapi import APIRouter, Depends
from starlette import status

from main_schemas import ResponseErrorBody
from web.auth.refresh_token import router as refresh_router
from web.users.routers import router as users_router
from web.certificates.routers import router as certificates_router
from web.users.schemas import UserCreate, UserRead
from web.users.users import auth_backend, current_superuser, fastapi_users

api_v1_router = APIRouter(
    prefix='/api/v1',
    dependencies=[],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'model': ResponseErrorBody,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            'model': ResponseErrorBody,
        },
    },
)

api_v1_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['auth'],
)
api_v1_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
    dependencies=[Depends(current_superuser)],
)

api_v1_router.include_router(users_router)
api_v1_router.include_router(refresh_router)
api_v1_router.include_router(certificates_router)
