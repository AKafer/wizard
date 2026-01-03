from typing import TYPE_CHECKING

from aiokafka import AIOKafkaProducer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from database.session import Session

if TYPE_CHECKING:
    from core.simple_cache import Cache


async def get_db_session() -> AsyncSession:
    async with Session() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_cache(request: Request) -> 'Cache':
    return request.app.state.cache


def get_kafka_producer(request: Request) -> AIOKafkaProducer:
    return request.app.state.kafka_producer
