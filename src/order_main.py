import logging
logging.basicConfig(level=logging.INFO)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from debug_toolbar.middleware import DebugToolbarMiddleware
from src.redis import close_redis
from src.rabbitmq import RabbitMQClient
from src.interfaces.routers.order import router as order_router
from src.infrastructure.services.menu_events import MenuEventService
from src.infrastructure.repositories.order import OrderRepository
from src.database import get_db

logger = logging.getLogger(__name__)

rabbitmq_client = RabbitMQClient()
menu_event_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global menu_event_service
    try:
        await rabbitmq_client.connect()
        logger.info("Successfully connected to RabbitMQ")
        
        channel = await rabbitmq_client._channel.declare_exchange(
            "menu_events",
            "topic",
            durable=True
        )
        logger.info("Successfully declared menu_events exchange")
        
        order_repository = OrderRepository(get_db())
        menu_event_service = MenuEventService(rabbitmq_client, order_repository)
        logger.info("Successfully initialized menu event service")
        
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        raise
        
    yield
    
    await close_redis()
    await rabbitmq_client.close()
    
app = FastAPI(lifespan=lifespan)

app.add_middleware(DebugToolbarMiddleware)

app.include_router(order_router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )



