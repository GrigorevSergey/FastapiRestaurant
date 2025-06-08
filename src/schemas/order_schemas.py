from datetime import datetime
from pydantic import BaseModel

from src.infrastructure.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    order_id: int
    item_id: int
    quantity: int
    price: int


class OrderCreate(BaseModel):
    user_id: int
    total_price: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemCreate]
    
class OrderItemUpdate(BaseModel):
    quantity: int
    price: int
    
class OrderUpdate(BaseModel):
    total_price: int
    status: OrderStatus
    updated_at: datetime
    
class OrderItemCreate(BaseModel):
    order_id: int
    dish_id: int
    quantity: int
    price: int
    
class BasketUpdate(BaseModel):
    quantity: int
    
    
class BasketCreate(BaseModel):
    user_id: int
    dish_id: int
    quantity: int
    
class OrderItem(BaseModel):
    id: int
    order_id: int
    item_id: int
    quantity: int
    price: int
    