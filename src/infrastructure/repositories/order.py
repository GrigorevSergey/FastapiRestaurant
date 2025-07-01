from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.schemas.order_schemas import OrderItemCreate, OrderItemUpdate, OrderCreate, OrderUpdate, BasketCreate, BasketUpdate
from src.infrastructure.models.order import Order, OrderItem, Basket, OrderStatus
from src.redis import cache, invalidate_cache
import datetime


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_order_id(self, order_id: int) -> Order | None:
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .filter(Order.id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def get_orders(self, limit: int = 10, offset: int = 0) -> list[Order]:    
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create_order(self, order: OrderCreate) -> Order:
        db_order = Order(
            user_id=order.user_id,
            total_price=order.total_price,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
            items=order.items
        )
        self.session.add(db_order)
        await self.session.commit()
        await self.session.refresh(db_order)
        await invalidate_cache("get_order_id*")
        return db_order 
    
    async def update_order(self, order_id: int, order: OrderUpdate) -> Order | None:
        db_order = await self.get_order_id(order_id)
        if not db_order:
            return None
        db_order.total_price = order.total_price
        db_order.status = order.status
        db_order.updated_at = order.updated_at
        await self.session.commit()
        await invalidate_cache("get_order_id*")
        return db_order
    
    async def delete_order(self, order_id: int) -> bool:
        db_order = await self.get_order_id(order_id)
        if not db_order:
            return False
        await self.session.delete(db_order)
        await self.session.commit()
        await invalidate_cache("get_order_id*")
        return True
    
    async def get_order_item_id(self, order_id: int) -> OrderItem | None:
        result = await self.session.execute(
            select(OrderItem).filter(OrderItem.id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def get_order_items(self, limit: int = 10, offset: int = 0) -> list[OrderItem]:
        result = await self.session.execute(
            select(OrderItem).offset(offset).limit(limit)
        )
        return result.scalars().all()
    
    async def create_order_item(self, order_item: OrderItemCreate) -> OrderItem:
        db_order_item = OrderItem(
            order_id=order_item.order_id,
            dish_id=order_item.dish_id,
            quantity=order_item.quantity,
            price=order_item.price
        )
        self.session.add(db_order_item)
        await self.session.commit()
        await self.session.refresh(db_order_item)
        await invalidate_cache("get_order_item_id*")
        return db_order_item
    
    async def update_order_item(self, order_item_id: int, order_item: OrderItemUpdate) -> OrderItem | None:
        db_order_item = await self.get_order_item_id(order_item_id)
        if not db_order_item:
            return None
        db_order_item.quantity = order_item.quantity
        db_order_item.price = order_item.price
        await self.session.commit()
        await invalidate_cache("get_order_item_id*")
        return db_order_item
    
    async def delete_order_item(self, order_item_id: int) -> bool:
        db_order_item = await self.get_order_item_id(order_item_id)
        if not db_order_item:
            return False
        await self.session.delete(db_order_item)
        await self.session.commit()
        await invalidate_cache("get_order_item_id*")
        return True
    
    async def get_basket_id(self, basket_id: int) -> Basket | None:
        result = await self.session.execute(
            select(Basket).filter(Basket.id == basket_id)
        )
        return result.scalar_one_or_none()
    
    async def get_baskets(self, limit: int = 10, offset: int = 0) -> list[Basket]:
        result = await self.session.execute(
            select(Basket).offset(offset).limit(limit)
        )
        return result.scalars().all()
    
    async def create_basket(self, basket: BasketCreate) -> Basket:
        db_basket = Basket(
            user_id=basket.user_id,
            item_id=basket.dish_id,  # исправлено: item_id вместо dish_id
            quantity=basket.quantity,
            price=0  # TODO: получить цену из menu, если нужно
        )
        self.session.add(db_basket)
        await self.session.commit()
        await self.session.refresh(db_basket)
        await invalidate_cache("get_basket_id*")
        return db_basket
    
    async def update_basket(self, basket_id: int, basket: BasketUpdate) -> Basket | None:
        db_basket = await self.get_basket_id(basket_id)
        if not db_basket:
            return None
        db_basket.quantity = basket.quantity
        await self.session.commit()
        await invalidate_cache("get_basket_id*")
        return db_basket
    
    async def delete_basket(self, basket_id: int) -> bool:
        db_basket = await self.get_basket_id(basket_id)
        if not db_basket:
            return False
        await self.session.delete(db_basket)
        await self.session.commit()
        await invalidate_cache("get_basket_id*")
        return True

    async def get_user_basket(self, user_id: int) -> list[Basket]:
        result = await self.session.execute(
            select(Basket).filter(Basket.user_id == user_id)
        )
        return result.scalars().all()

    async def basket_to_order(self, user_id: int) -> Order:
        basket_items = await self.get_user_basket(user_id)
        if not basket_items:
            raise ValueError("Корзина пуста")

        total_price = sum(item.price * item.quantity for item in basket_items)

        db_order = Order(
            user_id=user_id,
            total_price=total_price,
            status=OrderStatus.PENDING,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )
        self.session.add(db_order)
        await self.session.flush()

        order_items = []
        for basket_item in basket_items:
            order_item = OrderItem(
                order_id=db_order.id,
                dish_id=basket_item.item_id,
                quantity=basket_item.quantity,
                price=basket_item.price
            )
            order_items.append(order_item)
            self.session.add(order_item)

        for basket_item in basket_items:
            await self.delete_basket(basket_item.id)

        await self.session.commit()
        await self.session.refresh(db_order)
        await invalidate_cache("get_order_id*")
        return db_order
    
    async def cancel_order(self, order_id: str):
        order = await self.get_order_id(order_id)
        if order:
            order.status = OrderStatus.CANCELLED
            await self.db.commit()

