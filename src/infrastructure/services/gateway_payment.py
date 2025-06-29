import hmac
import hashlib
import base64
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")


def generate_token(order_id: str) -> str:
    message = f"{order_id}{SECRET_KEY}"
    token = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()
    return token


def verify_token(invoice_id: str, token: str) -> bool:
    expected_token = generate_token(invoice_id)
    return hmac.compare_digest(expected_token, token)


async def create_payment(amount: int, invoice_id: int) -> Dict[str, Any]:
    try:
        token = generate_token(str(invoice_id))
        print(f"Токен: {token[:20]}...")
        
        mock_response = {
            "success": True,
            "transaction_id": f"test_txn_{invoice_id}_{hash(str(amount))%10000}",
            "amount": amount,
            "order_id": invoice_id,
            "status": "pending",
            "payment_url": f"https://test-payment.local/pay?token={token}",
            "message": "Платеж создан успешно (ТЕСТ)"
        }
        
        print(f"Результат: {mock_response}")
        logger.info(f"Создан тестовый платеж для заказа {invoice_id} на сумму {amount}")

        return mock_response
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": "Ошибка создания платежа",
            "details": str(e)
        }
        print(f"Ошибка: {error_response}")
        logger.error(f"Ошибка создания платежа: {e}")
        return error_response


async def handle_cloudpayments_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        print(f"Получен webhook:")
        print(f"Payload: {payload}")
        
        transaction_id = payload.get("transaction_id", "unknown")
        status = payload.get("status", "unknown")
        invoice_id = payload.get("invoice_id", "unknown")
        amount = payload.get("amount", 0)
        
        print(f"Transaction ID: {transaction_id}")
        print(f"Статус: {status}")
        print(f"Заказ ID: {invoice_id}")
        print(f"Сумма: {amount}")
        
        if status.lower() in ["success", "completed", "paid"]:
            result = {
                "status": "processed",
                "message": "Платеж успешно завершен",
                "transaction_id": transaction_id,
                "invoice_id": invoice_id
            }
            print(f"Платеж успешен!")
            logger.info(f"Webhook: успешный платеж {transaction_id} для заказа {invoice_id}")

        elif status.lower() in ["failed", "error", "declined"]:
            result = {
                "status": "processed", 
                "message": "Платеж отклонен",
                "transaction_id": transaction_id,
                "invoice_id": invoice_id
            }
            print(f"Платеж отклонен!")
            logger.warning(f"Webhook: отклоненный платеж {transaction_id} для заказа {invoice_id}")

        elif status.lower() in ["cancelled", "canceled"]:
            result = {
                "status": "processed",
                "message": "Платеж отменен",
                "transaction_id": transaction_id,
                "invoice_id": invoice_id
            }
            print(f"Платеж отменен!")
            logger.info(f"Webhook: отмененный платеж {transaction_id} для заказа {invoice_id}")

        else:
            result = {
                "status": "ignored",
                "message": f"Неизвестный статус: {status}",
                "transaction_id": transaction_id,
                "invoice_id": invoice_id
            }
            print(f"Неизвестный статус: {status}")
            logger.warning(f"Webhook: неизвестный статус {status} для транзакции {transaction_id}")
        
        print(f"Ответ: {result}")
        return result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "message": f"Ошибка обработки webhook: {str(e)}"
        }
        print(f"Ошибка обработки webhook: {e}")
        logger.error(f"Ошибка обработки webhook: {e}")
        return error_result


def get_payment_status(transaction_id: str) -> Dict[str, Any]:
    print(f"Проверка статуса платежа:")
    print(f"Transaction ID: {transaction_id}")
    
    mock_status = {
        "transaction_id": transaction_id,
        "status": "completed" if "test_txn" in transaction_id else "pending",
        "amount": 150000,  
        "message": "Статус получен (ТЕСТ)"
    }
    
    print(f"Статус: {mock_status}")
    logger.info(f"Проверен статус платежа {transaction_id}")
    
    return mock_status