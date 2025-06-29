import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositories.payment import PaymentRepository
from src.infrastructure.services.gateway_payment import create_payment, handle_cloudpayments_webhook
from src.schemas.payment_schemas import PaymentCreate, PaymentUpdate, PaymentResponse
from src.infrastructure.models.payment import PaymentStatus

logger = logging.getLogger(__name__)


class PaymentService:    
    def __init__(self, session: AsyncSession):
        self.payment_repo = PaymentRepository(session)
    
    async def create_payment_for_order(self, invoice_id: int, amount: int, payment_method: str = "CARD") -> PaymentResponse:
        try:
            print(f"PaymentService: Создание платежа для заказа {invoice_id}")
            
            existing_payment = await self.payment_repo.get_payment_by_order_id(invoice_id)
            if existing_payment:
                logger.warning(f"Платеж для заказа {invoice_id} уже существует")
                return PaymentResponse.model_validate(existing_payment)
            
            payment_create = PaymentCreate(
                invoice_id=invoice_id,
                amount=amount
            )
            
            db_payment = await self.payment_repo.create_payment(payment_create)

            gateway_result = await create_payment(amount, invoice_id)

            if gateway_result.get("success"):
                update_data = PaymentUpdate(
                    status=PaymentStatus.PENDING,
                    transaction_id=gateway_result.get("transaction_id"),
                )
                db_payment = await self.payment_repo.update_payment(db_payment.id, update_data)
                print(f"Платеж создан успешно: ID {db_payment.id}")
            else:
                update_data = PaymentUpdate(
                    status=PaymentStatus.FAILED,
                )
                db_payment = await self.payment_repo.update_payment(db_payment.id, update_data)
                print(f"Ошибка создания платежа в платежной системе")
            
            return PaymentResponse.model_validate(db_payment)
            
        except Exception as e:
            logger.error(f"Ошибка создания платежа для заказа {invoice_id}: {e}")
            raise
    
    async def get_payment_by_id(self, payment_id: int) -> Optional[PaymentResponse]:
        try:
            payment = await self.payment_repo.get_payment_by_id(payment_id)
            if payment:
                return PaymentResponse.model_validate(payment)
            return None
        except Exception as e:
            logger.error(f"Ошибка получения платежа {payment_id}: {e}")
            raise
    
    async def get_payment_by_order_id(self, order_id: int) -> Optional[PaymentResponse]:
        try:
            payment = await self.payment_repo.get_payment_by_order_id(order_id)
            if payment:
                return PaymentResponse.model_validate(payment)
            return None
        except Exception as e:
            logger.error(f"Ошибка получения платежа для заказа {order_id}: {e}")
            raise
    
    async def process_webhook(self, payload: dict) -> dict:
        try:
            print(f"PaymentService: Обработка webhook")
            
            result = await handle_cloudpayments_webhook(payload)
            
            invoice_id = payload.get("order_id")
            transaction_id = payload.get("transaction_id")
            status = payload.get("status", "").lower()
            
            if invoice_id:
                payment = await self.payment_repo.get_payment_by_order_id(invoice_id)
                if payment:
                    new_status = PaymentStatus.PENDING
                    if status in ["success", "completed", "paid"]:
                        new_status = PaymentStatus.COMPLETED
                    elif status in ["failed", "error", "declined"]:
                        new_status = PaymentStatus.FAILED
                    elif status in ["cancelled", "canceled"]:
                        new_status = PaymentStatus.CANCELLED
                    
                    update_data = PaymentUpdate(
                        status=new_status,
                        transaction_id=transaction_id
                    )
                    await self.payment_repo.update_payment(payment.id, update_data)
                    print(f"Обновлен статус платежа {payment.id} -> {new_status}")
                else:
                    logger.warning(f"Платеж для заказа {invoice_id} не найден при обработке webhook")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка обработки webhook: {e}")
            raise
    
    async def update_payment_status(self, payment_id: int, status: PaymentStatus, transaction_id: Optional[str] = None) -> PaymentResponse:
        try:
            update_data = PaymentUpdate(
                status=status,
                transaction_id=transaction_id
            )
            
            updated_payment = await self.payment_repo.update_payment(payment_id, update_data)
            print(f"Обновлен статус платежа {payment_id} -> {status}")
            
            return PaymentResponse.model_validate(updated_payment)
            
        except Exception as e:
            logger.error(f"Ошибка обновления статуса платежа {payment_id}: {e}")
            raise