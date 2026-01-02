import asyncio
import logging
from contextlib import asynccontextmanager
from logging import config as logging_config

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse
from starlette.staticfiles import StaticFiles

import settings
from core.simple_cache import Cache
from routers import api_v1_router
from scripts.status_checker import daily_job

logger = logging.getLogger('control')


def setup_routes(app: FastAPI):
    app.include_router(api_v1_router)
    app.add_route('/ping/', lambda _request: PlainTextResponse('pong'))


origins = settings.ORIGIN_HOSTS

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cache = Cache(settings.REDIS_URL, namespace='wizard',)
    try:
        await app.state.cache.set("init:ping", "1", ttl=5)
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.exception("Redis connect failed: %s", e)

    app.state.daily_task = asyncio.create_task(daily_job())

    yield

    app.state.daily_task.cancel()
    try:
        await app.state.daily_task
    except asyncio.CancelledError:
        pass

    await app.state.cache.close()



def create_app() -> FastAPI:
    app = FastAPI(
        debug=True,
        docs_url='/api/v1/docs',
        openapi_url='/api/openapi.json',
        lifespan=lifespan
    )
    setup_routes(app)
    add_pagination(app)
    app.mount(f'/api/{settings.STATIC_FOLDER}', StaticFiles(directory='static'), name='static')
    logging_config.dictConfig(settings.LOGGING)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    return app