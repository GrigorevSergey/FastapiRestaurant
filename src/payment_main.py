import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.interfaces.routers.payment import router as payment_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Payment Service API",
    description="Микросервис для обработки платежей",
    version="1.0.0")

app.include_router(payment_router)


@app.get("/")
async def root():
    return {
        "service": "Payment Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/payments/create",
            "/payments/webhook/cloudpayments",
            "/payments/{payment_id}",
            "/payments/status/{payment_id}"
        ]
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Необработанная ошибка: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "Произошла внутренняя ошибка сервера"
        }
    )
