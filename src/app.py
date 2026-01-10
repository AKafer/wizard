import asyncio
import logging
from contextlib import asynccontextmanager
from logging import config as logging_config

from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_pagination import add_pagination
from redis.asyncio import Redis
from starlette.responses import PlainTextResponse
from starlette.staticfiles import StaticFiles

import settings
from core.simple_cache import Cache
from routers import api_v1_router
from scripts.status_checker import (
    actualize_certificates,
    cancel_expired_transactions,
)

logger = logging.getLogger('wizard')


def setup_routes(app: FastAPI):
    app.include_router(api_v1_router)
    app.add_route('/ping/', lambda _request: PlainTextResponse('pong'))


origins = settings.ORIGIN_HOSTS


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cache = Cache(
        settings.REDIS_URL,
        namespace='wizard',
    )

    redis = Redis.from_url(
        settings.REDIS_URL, encoding='utf-8', decode_responses=True
    )
    await FastAPILimiter.init(redis)

    try:
        app.state.kafka_producer = AIOKafkaProducer(
            bootstrap_servers=f'{settings.KAFKA_BOOTSTRAP_HOST}:{settings.KAFKA_BOOTSTRAP_PORT}',
            client_id='wizard',
        )
        await app.state.kafka_producer.start()
        logger.info('✅ Kafka connected')
    except Exception as e:
        logger.exception('Kafka connect failed: %s', e)

    try:
        await app.state.cache.set('init:ping', '1', ttl=5)
        logger.info('✅ Redis connected')
    except Exception as e:
        logger.exception('Redis connect failed: %s', e)

    app.state.actualize_certificates_task = asyncio.create_task(
        actualize_certificates()
    )
    app.state.cancel_transactions_task = asyncio.create_task(
        cancel_expired_transactions()
    )

    yield

    for task in (
        app.state.actualize_certificates_task,
        app.state.cancel_transactions_task,
    ):
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    await app.state.cache.close()
    await redis.close()
    await app.state.kafka_producer.stop()


def create_app() -> FastAPI:
    app = FastAPI(
        debug=True,
        docs_url='/api/v1/docs',
        openapi_url='/api/openapi.json',
        lifespan=lifespan,
    )
    setup_routes(app)
    add_pagination(app)
    app.mount(
        f'/api/{settings.STATIC_FOLDER}',
        StaticFiles(directory='static'),
        name='static',
    )
    logging_config.dictConfig(settings.LOGGING)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    return app
