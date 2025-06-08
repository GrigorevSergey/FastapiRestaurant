from typing import Dict, Any, Optional
from src.rabbitmq import RabbitMQClient, MenuEventType
from src.infrastructure.models.menu import Dish, Category
from src.infrastructure.repositories.order import OrderRepository
import logging

logger = logging.getLogger(__name__)

class MenuEventService:
    def __init__(self, rabbitmq_client: RabbitMQClient, order_repository: OrderRepository):
        self.rabbitmq = rabbitmq_client
        self.order_repository = order_repository

    async def publish_dish_created(self, dish: Dish) -> None:
        event_data = {
            "dish_id": dish.id,
            "name": dish.name,
            "description": dish.description,
            "price": dish.price,
            "category_id": dish.category_id,
            "is_available": dish.is_available
        }
        await self.rabbitmq.publish_event(
            MenuEventType.MENU_DISH_CREATED,
            event_data,
            exchange_name="menu_events"
        )

    async def publish_menu_updated(self, category: Category) -> None:
        event_data = {
            "category_id": category.id,
            "name": category.name,
            "description": category.description,
            "dishes_count": len(category.dishes) if hasattr(category, 'dishes') else 0
        }
        await self.rabbitmq.publish_event(
            MenuEventType.MENU_UPDATED,
            event_data,
            exchange_name="menu_events"
        )

    async def publish_price_changed(self, dish: Dish, old_price: float) -> None:
        event_data = {
            "dish_id": dish.id,
            "name": dish.name,
            "old_price": old_price,
            "new_price": dish.price,
            "price_change_percent": ((dish.price - old_price) / old_price) * 100
        }
        await self.rabbitmq.publish_event(
            MenuEventType.MENU_PRICE_CHANGED,
            event_data,
            exchange_name="menu_events"
        )

    async def publish_availability_changed(self, dish: Dish, old_availability: bool) -> None:
        event_data = {
            "dish_id": dish.id,
            "name": dish.name,
            "old_availability": old_availability,
            "new_availability": dish.is_available,
            "category_id": dish.category_id
        }
        await self.rabbitmq.publish_event(
            MenuEventType.MENU_ITEM_AVAILABILITY,
            event_data,
            exchange_name="menu_events"
        )

    @RabbitMQClient.event_handler(MenuEventType.MENU_DISH_CREATED)
    async def handle_dish_created(self, data: Dict[str, Any]) -> None:
        logger.info(f"New dish created: {data['name']} (ID: {data['dish_id']})")


    @RabbitMQClient.event_handler(MenuEventType.MENU_UPDATED)
    async def handle_menu_updated(self, data: Dict[str, Any]) -> None:
        logger.info(f"Menu updated: category {data['name']} (ID: {data['category_id']})")

    @RabbitMQClient.event_handler(MenuEventType.MENU_PRICE_CHANGED)
    async def handle_price_changed(self, data: Dict[str, Any]) -> None:
        logger.info(
            f"Price changed for dish {data['name']}: "
            f"{data['old_price']} -> {data['new_price']} "
            f"({data['price_change_percent']:.2f}%)"
        )

    @RabbitMQClient.event_handler(MenuEventType.MENU_ITEM_AVAILABILITY)
    async def handle_availability_changed(self, data: Dict[str, Any]) -> None:
        logger.info(
            f"Availability changed for dish {data['name']}: "
            f"{data['old_availability']} -> {data['new_availability']}"
        )
