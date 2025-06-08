import logging
logging.basicConfig(level=logging.INFO)
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.rabbitmq import RabbitMQClient, MenuEventType
import asyncio


logger = logging.getLogger(__name__)

rabbitmq_client = RabbitMQClient()

async def process_message(data: dict, event_type: MenuEventType):
    try:
        logger.info(f"Received message: {data} with event type: {event_type}")
        if event_type == MenuEventType.MENU_DISH_CREATED:
            logger.info(f"New dish created: {data['name']} (ID: {data['dish_id']})")
        elif event_type == MenuEventType.MENU_UPDATED:
            logger.info(f"Menu updated: category {data['name']} (ID: {data['category_id']})")
        elif event_type == MenuEventType.MENU_PRICE_CHANGED:
            logger.info(f"Price changed for dish {data['name']}: {data['old_price']} -> {data['new_price']}")
        elif event_type == MenuEventType.MENU_ITEM_AVAILABILITY:
            logger.info(f"Availability changed for dish {data['name']}: {data['old_availability']} -> {data['new_availability']}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

async def connect_to_rabbitmq(max_retries=5, delay=2):
    for attempt in range(max_retries):
        try:
            await rabbitmq_client.connect()
            logger.info("Successfully connected to RabbitMQ")
            return
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Failed to connect to RabbitMQ (attempt {attempt + 1}/{max_retries}): {e}")
            await asyncio.sleep(delay)

async def consume_messages():
    try:
        logger.info("Starting consume_messages function")
        await connect_to_rabbitmq()
        logger.info("Successfully connected to RabbitMQ")
        
        queue_name = "some_service_queue"
        logger.info(f"Declaring queue: {queue_name}")

        await rabbitmq_client._channel.declare_exchange(
            "menu_events",
            "topic",
            durable=True
        )
        logger.info("Exchange menu_events объявлен (или уже существует)")

        try:
            logger.info("Attempting to bind queue to exchange")
            for event_type in MenuEventType:
                await rabbitmq_client.bind_queue_to_exchange(
                    queue_name=queue_name,
                    exchange_name="menu_events",
                    routing_key=event_type
                )
                logger.info(f"Successfully bound queue to exchange with routing key: {event_type}")
        except Exception as bind_error:
            logger.error(f"Error binding queue to exchange: {bind_error}")
            raise
        
        try:
            logger.info("Starting to consume events")
            await rabbitmq_client.consume_events(
                queue_name=queue_name,
                callback=process_message
            )
            logger.info(f"Successfully started consuming messages from queue: {queue_name}")
        except Exception as consume_error:
            logger.error(f"Error consuming events: {consume_error}")
            raise
        
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error in consume_messages: {e}")
        logger.exception("Full traceback:")
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting application lifespan")
        consume_task = asyncio.create_task(consume_messages())
        consume_task.add_done_callback(lambda t: logger.error(f"Consume task failed: {t.exception()}") if t.exception() else None)
        logger.info("Consume task started")
        yield
    except Exception as e:
        logger.error(f"Error in lifespan: {e}")
        logger.exception("Full traceback:")
        raise
    finally:
        logger.info("Shutting down application")
        await rabbitmq_client.close()
        logger.info("Application shutdown complete")

app = FastAPI(
    title="Some Service",
    description="Сервис для обработки сообщений от Menu Service",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 