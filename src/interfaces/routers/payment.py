import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.dependencies import get_db
from src.infrastructure.services.payment_service import PaymentService
from src.schemas.payment_schemas import PaymentCreateRequest, PaymentResponse, WebhookPayload
from src.infrastructure.models.payment import PaymentStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


def get_payment_service(db: AsyncSession = Depends(get_db)) -> PaymentService:
    return PaymentService(db)


@router.post("/create", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_request: PaymentCreateRequest,
    payment_service: PaymentService = Depends(get_payment_service)
):
    try:        
        payment = await payment_service.create_payment_for_order(
            invoice_id=payment_request.invoice_id,
            amount=payment_request.amount,
        )

        logger.info(f"Создан платеж ID: {payment.id} для заказа {payment_request.invoice_id}")
        return payment
        
    except Exception as e:
        logger.error(f"Ошибка создания платежа: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка создания платежа: {str(e)}"
        )

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    payment_service: PaymentService = Depends(get_payment_service)
):
    try:
        payment = await payment_service.get_payment_by_id(payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Платеж с ID {payment_id} не найден"
            )
        return payment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения платежа {payment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get("/order/{order_id}", response_model=PaymentResponse)
async def get_payment_by_order(
    order_id: int,
    payment_service: PaymentService = Depends(get_payment_service)
):
    try:
        payment = await payment_service.get_payment_by_order_id(order_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Платеж для заказа {order_id} не найден"
            )
        return payment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения платежа для заказа {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post("/webhook/cloudpayments")
async def cloudpayments_webhook(
    request: Request,
    payment_service: PaymentService = Depends(get_payment_service)):
    try:
        payload = await request.json()
        print(f"Получен webhook от CloudPayments")
        
        result = await payment_service.process_webhook(payload)
        
        logger.info(f"Обработан webhook: {result}")
        return {"status": "success", "message": "Webhook обработан", "result": result}
        
    except Exception as e:
        logger.error(f"Ошибка обработки webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка обработки webhook: {str(e)}"
        )


@router.put("/{payment_id}/status")
async def update_payment_status(
    payment_id: int,
    status: PaymentStatus,
    transaction_id: str = None,
    payment_service: PaymentService = Depends(get_payment_service)
):
    try:
        payment = await payment_service.update_payment_status(
            payment_id=payment_id,
            status=status,
            transaction_id=transaction_id
        )
        
        logger.info(f"Обновлен статус платежа {payment_id} -> {status}")
        return payment
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Ошибка обновления статуса платежа {payment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )