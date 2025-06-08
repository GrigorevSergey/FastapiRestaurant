import datetime
from pydantic import BaseModel, ConfigDict
from src.infrastructure.models.order import OrderStatus


class OrderItem(BaseModel):
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
    
    
class Basket(BaseModel):
    id: int
    user_id: int
    item_id: int
    quantity: int
    price: int
    

class Order(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        populate_by_name=True
    )
    
    id: int
    user_id: int
    total_price: int
    status: OrderStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime
    items: list[OrderItem]
    