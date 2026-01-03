import asyncio
from typing import Any, Dict, Type

from aiokafka import AIOKafkaConsumer

import settings


class AsyncKafkaBaseWorker:
    """
    Async base worker class to communicate with Apache Kafka
    """

    def __init__(
        self,
        config: Dict[str, Any],
        *,
        key_deserializer: None,
        value_deserializer: None,
    ):
        self.topics = self.get_topics()
        self.consumer = AIOKafkaConsumer(*self.topics, **config)
        self.key_deserializer = key_deserializer
        self.value_deserializer = value_deserializer
        self.group = config.get('group_id', 'unknown')

    @staticmethod
    def get_topics():
        raise NotImplementedError

    async def run(self):
        await self.consumer.start()

        try:
            async for message in self.consumer:
                try:
                    if self.key_deserializer and message.key is not None:
                        message.key = await self.key_deserializer.deserialize(
                            message.key
                        )
                    if self.value_deserializer and message.value is not None:
                        message.value = (
                            await self.value_deserializer.deserialize(
                                message.value
                            )
                        )

                    await self.handle(message)

                    if not self.consumer._enable_auto_commit:  # noqa: SLF001
                        await self.consumer.commit()

                except Exception:
                    raise

        finally:
            await self.consumer.stop()

    async def handle(self, message):
        raise NotImplementedError


class AsyncKafkaWorkerRunner:
    worker_class: Type[AsyncKafkaBaseWorker]

    def run(self):
        asyncio.run(self._arun())

    async def _arun(self):
        config = self.get_consumer_config()

        worker_instance = self.worker_class(
            config,
            key_deserializer=self.get_key_deserializer(),
            value_deserializer=self.get_value_deserializer(),
        )
        await worker_instance.run()

    def get_consumer_config(self) -> Dict[str, Any]:
        return {
            'bootstrap_servers': f'{settings.KAFKA_BOOTSTRAP_HOST}:{settings.KAFKA_BOOTSTRAP_PORT}',
            'group_id': settings.KAFKA_GROUP_ID,
            'auto_offset_reset': 'earliest',
            'enable_auto_commit': False,
            'client_id': 'wizard',
        }

    def get_key_deserializer(self) -> None:
        return None

    def get_value_deserializer(self) -> None:
        return None
