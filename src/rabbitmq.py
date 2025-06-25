from typing import Any, Callable, Dict, Optional
import json
import aio_pika
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractQueue, AbstractExchange
from functools import wraps
from src.core.config import settings
import logging
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)

class EventType(str, Enum):
    MENU_UPDATED = "menu.updated"
    MENU_PRICE_CHANGED = "menu.price.change"
    MENU_DISH_CREATED = "menu.dish.created"
    MENU_ITEM_AVAILABILITY = "menu.item.availability"
    ORDER_DELAYED = "order.delayed"
    ORDER_CREATED = "order.created"
    ORDER_FAILED = "order.failed"
    MENU_RESERVED = "menu.reserved"
    MENU_FAILED = "menu.failed"

class RabbitMQClient:
    def __init__(
        self,
        host: str = settings.RABBITMQ_HOST,
        port: int = settings.RABBITMQ_PORT,
        username: str = settings.RABBITMQ_USER,
        password: str = settings.RABBITMQ_PASSWORD,
        virtualhost: str = settings.RABBITMQ_VHOST
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.virtualhost = virtualhost
        self._connection: Optional[AbstractConnection] = None
        self._channel: Optional[AbstractChannel] = None
        self._queues: Dict[str, AbstractQueue] = {}
        self._exchanges: Dict[str, AbstractExchange] = {}
        self._consumers: Dict[str, Callable] = {}
        logger.info(f"RabbitMQClient инициализирован: host={host}, port={port}, vhost={virtualhost}")

    async def connect(self) -> None:
        logger.info("[RabbitMQ] Подключение...")
        max_retries = 10
        base_delay = 5
        for attempt in range(max_retries):
            try:
                self._connection = await aio_pika.connect_robust(
                    host=self.host,
                    port=self.port,
                    login=self.username,
                    password=self.password,
                    virtualhost=self.virtualhost
                )
                self._channel = await self._connection.channel()
                logger.info("Successfully connected to RabbitMQ")
                logger.info("[RabbitMQ] Подключение завершено")
                return
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to connect to RabbitMQ after {max_retries} attempts: {e}")
                    raise
                delay = base_delay * (attempt + 1)
                logger.warning(f"Failed to connect to RabbitMQ (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)

    async def close(self) -> None:
        logger.info("[RabbitMQ] Закрытие соединения...")
        if self._connection:
            await self._connection.close()
            logger.info("RabbitMQ connection closed")
            logger.info("[RabbitMQ] Соединение закрыто")

    async def declare_queue(self, queue_name: str) -> AbstractQueue:
        logger.info(f"[RabbitMQ] Объявление очереди: {queue_name}")
        if queue_name not in self._queues:
            queue = await self._channel.declare_queue(
                queue_name,
                durable=True,
                auto_delete=False
            )
            self._queues[queue_name] = queue
        logger.info(f"[RabbitMQ] Очередь объявлена: {queue_name}")
        return self._queues[queue_name]

    async def get_exchange(self, exchange_name: str) -> AbstractExchange:
        logger.info(f"[RabbitMQ] Получение/создание exchange: {exchange_name}")
        if exchange_name not in self._exchanges:
            exchange = await self._channel.get_exchange(exchange_name)
            self._exchanges[exchange_name] = exchange
        logger.info(f"[RabbitMQ] Exchange готов: {exchange_name}")
        return self._exchanges[exchange_name]

    async def bind_queue_to_exchange(
        self,
        queue_name: str,
        exchange_name: str,
        routing_key: str
    ) -> None:
        logger.info(f"[RabbitMQ] Биндинг очереди {queue_name} к exchange {exchange_name} с routing_key {routing_key}")
        if not self._channel:
            raise RuntimeError("RabbitMQ channel is not initialized")
            
        queue = await self.declare_queue(queue_name)
        exchange = await self.get_exchange(exchange_name)
        await queue.bind(exchange, routing_key)
        logger.info(f"[RabbitMQ] Биндинг завершён: {queue_name} <-> {exchange_name} [{routing_key}]")

    async def publish_event(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        exchange_name: str = "amq.topic",
        routing_key: Optional[str] = None
    ) -> None:
        logger.info(f"[RabbitMQ] Публикация события {event_type} в exchange {exchange_name} с routing_key {routing_key or event_type} и данными: {data}")
        if not self._channel:
            raise RuntimeError("RabbitMQ channel is not initialized")

        message = aio_pika.Message(
            body=json.dumps(data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
            headers={"event_type": event_type}
        )

        exchange = await self.get_exchange(exchange_name)
        await exchange.publish(
            message,
            routing_key=routing_key or event_type,
            mandatory=True
        )
        logger.info(f"[RabbitMQ] Событие опубликовано: {event_type}")

    async def publish_delayed(
        self,
        data: Dict[str, Any],
        exchange_name: str = "amq.topic",
        routing_key: str = EventType.ORDER_DELAYED
    ) -> None:
        logger.info(f"[RabbitMQ] Публикация отложенного события в exchange {exchange_name} с routing_key {routing_key} и данными: {data}")
        if not self._channel:
            raise RuntimeError("RabbitMQ channel is not initialized")

        message = aio_pika.Message(
            body=json.dumps(data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
            headers={"event_type": EventType.ORDER_DELAYED},
            expiration=3600000 
        )

        exchange = await self.get_exchange(exchange_name)
        await exchange.publish(
            message,
            routing_key=routing_key,
            mandatory=True
        )
        logger.info(f"[RabbitMQ] Отложенное событие опубликовано: {routing_key}")

    async def consume_events(
        self,
        queue_name: str,
        callback: Callable[[Dict[str, Any], EventType], None]
    ) -> None:
        logger.info(f"[RabbitMQ] Запуск consume для очереди: {queue_name}")
        queue = await self.declare_queue(queue_name)
        
        async def process_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    data = json.loads(message.body.decode())
                    event_type = EventType(message.headers.get("event_type"))
                    await callback(data, event_type)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        await queue.consume(process_message)
        self._consumers[queue_name] = callback
        logger.info(f"[RabbitMQ] Consume запущен для очереди: {queue_name}")

    @classmethod
    def event_handler(cls, event_type: EventType):
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            wrapper.event_type = event_type
            return wrapper
        return decorator