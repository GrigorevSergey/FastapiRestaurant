from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.dependencies import get_current_user
from src.database import get_db
import httpx
from dotenv import load_dotenv
import os
from src.domain.order import OrderStatus
from src.schemas.order_schemas import OrderUpdate, BasketUpdate
from src.infrastructure.repositories.order import OrderRepository
from src.infrastructure.services.menu_events_service import menu_event_service
from pydantic import BaseModel, ConfigDict
from fastapi_limiter.depends import RateLimiter


load_dotenv()
MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL")

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

@router.get("/orders", response_model=list[OrderResponse],
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
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
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user = await menu_event_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    order = await OrderRepository(db).create_order(user_id)
    return order

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
    user_id: int = Depends(get_current_user),
    dish_id: int = Query(..., description="ID блюда"),
    quantity: int = Query(..., description="Количество")
):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MENU_SERVICE_URL}/dishes/{dish_id}")
        dish = response.json()
        if not dish:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")
        basket = await OrderRepository(db).create_basket(user_id, dish_id, quantity)
    return basket

@router.put("/baskets/{basket_id}", response_model=BasketResponse,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_basket(
    basket_id: int,
    basket: BasketUpdate,
    db: AsyncSession = Depends(get_db)
):
    basket = await OrderRepository(db).update_basket(basket_id, basket)
    return basket

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

