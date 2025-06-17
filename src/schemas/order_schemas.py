from datetime import datetime
from pydantic import BaseModel, ConfigDict

from src.infrastructure.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    order_id: int
    item_id: int
    quantity: int
    price: int


class OrderCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    total_price: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemCreate]
    
class OrderItemUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    quantity: int
    price: int
    
class OrderUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    total_price: int
    status: OrderStatus
    updated_at: datetime
    
class OrderItemCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    order_id: int
    dish_id: int
    quantity: int
    price: int
    
class BasketUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    quantity: int
    
    
class BasketCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    dish_id: int
    quantity: int
    
class OrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_id: int
    item_id: int
    quantity: int
    price: int
    