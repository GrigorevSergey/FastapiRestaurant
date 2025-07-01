from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.schemas.payment_schemas import PaymentCreate, PaymentUpdate
from src.infrastructure.models.payment import Payment, PaymentStatus
from src.redis import cache, invalidate_cache
import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_payments(self, limit: int = 10, offset: int = 0) -> list[Payment]:
        try:
            result = await self.session.execute(
                select(Payment)
                .offset(offset)
                .limit(limit)
                .order_by(Payment.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Ошибка получения списка платежей: {e}")
            raise

    @cache()
    async def get_payment_by_id(self, payment_id: int) -> Payment | None:
        try:
            result = await self.session.execute(
                select(Payment)
                .filter(Payment.id == payment_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Ошибка получения платежа по ID {payment_id}: {e}")
            raise

    async def get_payment_by_order_id(self, order_id: int) -> Payment | None:
        try:
            result = await self.session.execute(
                select(Payment)
                .filter(Payment.invoice_id == order_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Ошибка получения платежа по order_id {order_id}: {e}")
            raise

    async def create_payment(self, payment: PaymentCreate) -> Payment:
        try:
            now = datetime.datetime.now()
            db_payment = Payment(
                invoice_id=payment.invoice_id,
                amount=payment.amount,
                status=PaymentStatus.PENDING,
                created_at=now,
                updated_at=now
            )
            self.session.add(db_payment)
            await self.session.commit()
            await self.session.refresh(db_payment)
            await invalidate_cache("get_payment_by_id*")
            
            logger.info(f"Создан платеж ID: {db_payment.id} для заказа {payment.invoice_id}")
            return db_payment
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка создания платежа: {e}")
            raise

    async def update_payment(self, payment_id: int, payment: PaymentUpdate) -> Payment:
        try:
            db_payment = await self.session.get(Payment, payment_id)
            if not db_payment:
                raise ValueError(f"Платеж с ID {payment_id} не найден")
            
            for key, value in payment.model_dump(exclude_unset=True).items():
                if value is not None:
                    setattr(db_payment, key, value)
            
            db_payment.updated_at = datetime.datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(db_payment)
            await invalidate_cache("get_payment_by_id*")
            
            logger.info(f"Обновлен платеж ID: {payment_id}")
            return db_payment
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка обновления платежа {payment_id}: {e}")
            raise

    async def delete_payment(self, payment_id: int) -> None:
        try:
            db_payment = await self.session.get(Payment, payment_id)
            if db_payment:
                await self.session.delete(db_payment)
                await self.session.commit()
                await invalidate_cache("get_payment_by_id*")
                logger.info(f"Удален платеж ID: {payment_id}")
            else:
                logger.warning(f"Платеж ID: {payment_id} не найден для удаления")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка удаления платежа {payment_id}: {e}")
            raise