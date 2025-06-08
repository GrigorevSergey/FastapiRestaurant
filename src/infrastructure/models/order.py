from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Boolean, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from src.database import Base
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = {"schema": "orders"}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.users.id"), nullable=False)
    total_price = Column(Integer, nullable=False)
    status = Column(SQLEnum(OrderStatus), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    items = relationship("OrderItem", back_populates="order")
    
    
class Basket(Base):
    __tablename__ = "baskets"
    __table_args__ = {"schema": "orders"}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("menu.dishes.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    
    
class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = {"schema": "orders"}
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.orders.id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("menu.dishes.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    order = relationship("Order", back_populates="items")
    