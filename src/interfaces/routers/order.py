from datetime import datetime
import uuid
from fastapi import APIRouter, Body, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.models import order
from src.core.dependencies import get_current_user
from src.database import get_db
import httpx
from dotenv import load_dotenv
import os
from src.domain.order import OrderStatus
from src.schemas.order_schemas import OrderCreate, OrderUpdate, BasketUpdate
from src.infrastructure.repositories.order import OrderRepository
from pydantic import BaseModel, ConfigDict
from fastapi_limiter.depends import RateLimiter
from src.infrastructure.services.retry import RetryService
from src.rabbitmq import EventType, RabbitMQClient
import logging
from src.schemas.order_schemas import BasketCreate


logger = logging.getLogger(__name__)
rabbit = RabbitMQClient()

load_dotenv()
MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL")


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        populate_by_name=True
    )
    
    id: int
    order_id: int
    item_id: int
    quantity: int
    price: int
        
class OrderResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        populate_by_name=True
    )
    
    id: int
    user_id: int
    total_price: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]
        
class BasketResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        populate_by_name=True
    )
    
    id: int
    user_id: int
    dish_id: int
    quantity: int


router = APIRouter(
    prefix="/order",
    tags=["order"],
)

async def process_order(order_id: str, user_id: int, items: list):
    user_service_ok = await RetryService.check_health(USER_SERVICE_URL)
    menu_service_ok = await RetryService.check_health(MENU_SERVICE_URL)
    payment_service_ok = await RetryService.check_health(PAYMENT_SERVICE_URL)
    if not user_service_ok or not menu_service_ok:
        await rabbit.publish_event(EventType.ORDER_FAILED, {
            "user_id": user_id,
            "order_id": order_id,
            "items": [item.dish_id for item in items]
        })
        return {"status": "failed"}
    try:
        user = await RetryService.get(f"{USER_SERVICE_URL}/users/{user_id}")
    except Exception as e:
        await rabbit.publish_event(EventType.ORDER_FAILED, {
            "user_id": user_id,
            "order_id": order_id,
            "items": [item.dish_id for item in items]
        })
        return {"status": "failed"}
    for item in items:
        try:
            dish = await RetryService.get(f"{MENU_SERVICE_URL}/dishes/{item.dish_id}")
            if not dish.get("is_available"):
                raise HTTPException(status_code=400, detail=f"Item {item.dish_id} is not available")
        except Exception as e:
            await rabbit.publish_event(EventType.ORDER_FAILED, {
                "user_id": user_id,
                "order_id": order_id,
                "items": [item.dish_id for item in items]
            })
            return {"order_id": order_id, "status": "failed"}
    
    await rabbit.publish_event(EventType.ORDER_CREATED, {
        "order_id": order_id,
        "user_id": user_id,
        "items": [item.dish_id for item in items]
    })
    return {"order_id": order_id, "status": "success"}


@router.get("/health")
async def health_check():
    return {"status": "healthy"}


@router.get("/orders", response_model=list[OrderResponse],
            )
async def get_orders(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(0, ge=0, description="Сдвиг записей"),
    offset: int = Query(10, ge=0, description="Лимит записей на странице")
):
    orders = await OrderRepository(db).get_orders(limit, offset)
    return orders

@router.get("/orders/{order_id}", response_model=OrderResponse,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    order = await OrderRepository(db).get_order_id(order_id)
    return order

@router.post("/orders", response_model=OrderResponse,
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_order(
    order: OrderCreate = Body(...),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    order_id = str(uuid.uuid4())
    result = await process_order(order_id, user_id, order.items)
    return result

@RabbitMQClient.event_handler(EventType.MENU_RESERVED)
async def handle_menu_reserved(data: dict, event_type: EventType):
    order_id = data["order_id"]
    logger.info(f"Order {order_id}: Items reserved successfully")

@RabbitMQClient.event_handler(EventType.MENU_FAILED)
async def handle_menu_failed(data: dict, event_type: EventType):
    order_id = data["order_id"]
    logger.info(f"Order {order_id}: Item reservation failed, initiating rollback")
    await rabbit.publish_event(EventType.ORDER_FAILED, {"order_id": order_id})

@RabbitMQClient.event_handler(EventType.ORDER_DELAYED)
async def handle_delayed_order(data: dict, event_type: EventType):
    order_id = data["order_id"]
    user_id = data["user_id"]
    items = data["items"]
    logger.info(f"Processing delayed order {order_id}")
    await process_order(order_id, user_id, items)

@RabbitMQClient.event_handler(EventType.ORDER_FAILED)
async def handle_order_failed(data: dict, event_type: EventType):
    order_id = data["order_id"]
    db = await get_db()
    await OrderRepository(db).cancel_order(order_id)
    logger.info(f"Order {order_id} cancelled due to saga failure")

@router.put("/orders/{order_id}", response_model=OrderResponse,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_order(
    order_id: int,
    order: OrderUpdate,
    db: AsyncSession = Depends(get_db)
): 
    order = await OrderRepository(db).update_order(order_id, order)
    return order

@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    await OrderRepository(db).delete_order(order_id)
    return {"message": "Order deleted successfully"}


@router.get("/baskets", response_model=list[BasketResponse],
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_baskets(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(0, ge=0, description="Сдвиг записей"),
    offset: int = Query(10, ge=0, description="Лимит записей на странице")
):
    baskets = await OrderRepository(db).get_baskets(limit, offset)
    return baskets

@router.get("/baskets/{basket_id}", response_model=BasketResponse,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_basket(
    basket_id: int,
    db: AsyncSession = Depends(get_db)
):
    basket = await OrderRepository(db).get_basket(basket_id)
    return basket

@router.post("/baskets", response_model=BasketResponse,
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_basket(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
    dish_id: int = Query(..., description="ID блюда"),
    quantity: int = Query(..., description="Количество")
):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MENU_SERVICE_URL}/dishes/{dish_id}")
        dish = response.json()
        if not dish:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")
        basket_create = BasketCreate(user_id=user.id, dish_id=dish_id, quantity=quantity)
        basket = await OrderRepository(db).create_basket(basket_create)
    # Приводим к BasketResponse с dish_id
    return BasketResponse(
        id=basket.id,
        user_id=basket.user_id,
        dish_id=basket.item_id,  # соответствие схеме
        quantity=basket.quantity
    )

@router.put("/baskets/{basket_id}", response_model=BasketResponse,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_basket(
    basket_id: int,
    basket: BasketUpdate,
    db: AsyncSession = Depends(get_db)
):
    basket = await OrderRepository(db).update_basket(basket_id, basket)
    if not basket:
        raise HTTPException(status_code=404, detail="Basket not found")
    return BasketResponse(
        id=basket.id,
        user_id=basket.user_id,
        dish_id=basket.item_id,
        quantity=basket.quantity
    )

@router.delete("/baskets/{basket_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def delete_basket(
    basket_id: int,
    db: AsyncSession = Depends(get_db)
):
    await OrderRepository(db).delete_basket(basket_id)
    return {"message": "Basket deleted successfully"}

@router.post("/baskets/bask-to-order", response_model=OrderResponse,
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def convert_basket_to_order(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        order = await OrderRepository(db).convert_basket_to_order(user_id)
        
        if PAYMENT_SERVICE_URL:
            try:
                print(f"Создание платежа для заказа {order.id}")
                async with httpx.AsyncClient() as client:
                    payment_data = {
                        "order_id": order.id,
                        "amount": order.total_price,
                    }
                    response = await client.post(
                        f"{PAYMENT_SERVICE_URL}/payments/create",
                        json=payment_data
                    )
                    if response.status_code == 201:
                        payment_info = response.json()
                        print(f"Платеж создан: {payment_info}")
                        logger.info(f"Создан платеж для заказа {order.id}: {payment_info}")
                    else:
                        print(f"Ошибка создания платежа: {response.text}")
                        logger.warning(f"Не удалось создать платеж для заказа {order.id}")
            except Exception as e:
                print(f"Ошибка при обращении к Payment Service: {e}")
                logger.error(f"Ошибка интеграции с Payment Service: {e}")
        
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании заказа"
        )


@router.get("/orders/{order_id}/payment")
async def get_order_payment(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        order = await OrderRepository(db).get_order_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заказ {order_id} не найден"
            )
        
        if PAYMENT_SERVICE_URL:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{PAYMENT_SERVICE_URL}/payments/order/{order_id}")
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return {"message": f"Платеж для заказа {order_id} не найден"}
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Ошибка получения информации о платеже"
                    )
        else:
            return {"message": "Payment Service недоступен"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения платежа для заказа {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

