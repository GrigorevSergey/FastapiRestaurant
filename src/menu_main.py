import logging
logging.basicConfig(level=logging.INFO)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from debug_toolbar.middleware import DebugToolbarMiddleware
from src.redis import close_redis
from src.rabbitmq import RabbitMQClient
from src.interfaces.routers.v1 import menu as menu_v1
from src.interfaces.routers.v2 import menu as menu_v2
from src.infrastructure.services.menu_events import MenuEventService

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
        
        menu_event_service = MenuEventService(rabbitmq_client)
        logger.info("Successfully initialized menu event service")
        
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        raise
    yield
    await close_redis()
    await rabbitmq_client.close()
    logger.info("Application shutdown complete")

app = FastAPI(lifespan=lifespan)

app = FastAPI(debug=True)
app.add_middleware(DebugToolbarMiddleware)

app.include_router(menu_v1.router, prefix="/menu1", tags=["menu v1"])
app.include_router(menu_v2.router, prefix="/menu2", tags=["menu v2"])

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

async def get_menu_event_service() -> MenuEventService:
    if menu_event_service is None:
        raise RuntimeError("Menu event service not initialized")
    return menu_event_service