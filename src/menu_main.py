import logging
logging.basicConfig(level=logging.INFO)
from fastapi import FastAPI, Request, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from debug_toolbar.middleware import DebugToolbarMiddleware
from src.redis import close_redis
from src.rabbitmq import RabbitMQClient
from src.interfaces.routers.v1 import menu as menu_v1
from src.interfaces.routers.v2 import menu as menu_v2
from src.infrastructure.services.menu_events import MenuEventService
from src.infrastructure.repositories.order import OrderRepository
from src.database import get_db
from src.infrastructure.services.menu_events_service import menu_event_service

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
        app.state.menu_event_service = menu_event_service
        logger.info("Successfully initialized menu event service")
        
        redis_connection = redis.from_url("redis://redis:6379")
        await FastAPILimiter.init(redis_connection)
        logger.info("Successfully initialized Redis connection")
        
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        raise
    yield
    await close_redis()
    await rabbitmq_client.close()
    logger.info("Application shutdown complete")

app = FastAPI(lifespan=lifespan)

app.add_middleware(DebugToolbarMiddleware)

@app.get("/")
async def root(request: Request):
    logger.info(f"Request headers at root endpoint: {dict(request.headers)}")
    
    try:
        return {
            "service": "Menu Service",
            "version": "1.0",
            "endpoints": [
                "/menu1/menu",
                "/menu2/menu"
            ],
            "request_info": {
                "client": request.client.host if request.client else "unknown",
                "method": request.method,
                "headers": {k: v for k, v in request.headers.items() if k.lower() != "authorization"}
            }
        }
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error processing request: {str(e)}"}
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(menu_v1.router, prefix="/menu1", tags=["menu v1"])
app.include_router(menu_v2.router, prefix="/menu2", tags=["menu v2"])

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

async def get_menu_event_service(request: Request) -> MenuEventService:
    service = getattr(request.app.state, "menu_event_service", None)
    if service is None:
        raise RuntimeError("Menu event service not initialized")
    return service