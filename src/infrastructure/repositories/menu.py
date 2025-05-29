from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.infrastructure.models.menu import Category, Dish, Tag
from src.domain.menu import CategoryCreate, DishCreate, CategoryUpdate, DishUpdate, TagCreate, TagUpdate


class MenuRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_category(self, category: CategoryCreate) -> Category:
        db_category = Category(
            name=category.name,
            description=category.description
        )
        self.session.add(db_category)
        await self.session.commit()
        await self.session.refresh(db_category)
        return db_category
    
    async def update_category(self, category_id: int, category: CategoryUpdate) -> Category | None:
        db_category = await self.get_category_by_id(category_id)
        if not db_category:
            return None
        db_category.name = category.name
        db_category.description = category.description
        await self.session.commit()
        await self.session.refresh(db_category)
        return db_category
    
    async def get_category_id(self, category_id: int) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
    
    async def get_categories(self, limit: int = 10, offset: int = 0) -> list[Category]:
        result = await self.session.execute(
            select(Category).offset(offset).limit(limit)
        )
        return result.scalars().all()
    
    async def delete_category(self, category_id: int) -> bool:  
        db_category = await self.get_category_by_id(category_id)
        if not db_category:
            return False
        await self.session.delete(db_category)
        await self.session.commit()
        return True

    async def create_dish(self, dish: DishCreate) -> Dish:
        db_dish = Dish(
            name=dish.name,
            description=dish.description,
            price=dish.price,
            category_id=dish.category_id
        )
        self.session.add(db_dish)
        await self.session.commit()
        await self.session.refresh(db_dish)
        return db_dish
    
    async def update_dish(self, dish_id: int, dish: DishUpdate) -> Dish | None:
        db_dish = await self.get_dish_by_id(dish_id)
        if not db_dish:
            return None
        db_dish.name = dish.name
        db_dish.description = dish.description
        db_dish.price = dish.price
        db_dish.category_id = dish.category_id
        await self.session.commit()
        await self.session.refresh(db_dish)
        return db_dish
    
    async def delete_dish(self, dish_id: int) -> bool:
        db_dish = await self.get_dish_by_id(dish_id)
        if not db_dish:
            return False
        await self.session.delete(db_dish)
        await self.session.commit()
        return True
    
    async def get_dish_id(self, dish_id: int) -> Dish | None:
        result = await self.session.execute(
            select(Dish).where(Dish.id == dish_id)
        )
        return result.scalar_one_or_none()
    
    async def get_dishes(self, limit: int = 10, offset: int = 0) -> list[Dish]:
        result = await self.session.execute(
            select(Dish).limit(limit).offset(offset)
        )
        return result.scalars().all()
    
    async def get_dishes_category_id(self, category_id: int) -> list[Dish]:
        result = await self.session.execute(
            select(Dish).where(Dish.category_id == category_id)
        )
        return result.scalars().all()
    
    async def get_tags(self, limit: int = 10, offset: int = 0) -> list[Tag]:
        result = await self.session.execute(
            select(Tag).limit(limit).offset(offset)
        )
        return result.scalars().all()
    
    async def get_tag_id(self, tag_id: int) -> Tag | None:
        result = await self.session.execute(
            select(Tag).where(Tag.id == tag_id)
        )
        return result.scalar_one_or_none()
    
    async def get_tag_name(self, tag_name: str) -> Tag | None:
        result = await self.session.execute(
            select(Tag).where(Tag.name == tag_name)
        )
        return result.scalar_one_or_none()
    
    async def create_tag(self, tag: TagCreate) -> Tag:
        db_tag = Tag(
            name=tag.name
        )
        self.session.add(db_tag)
        await self.session.commit()
        await self.session.refresh(db_tag)
        return db_tag
    
    async def update_tag(self, tag_id: int, tag: TagUpdate) -> Tag | None:  
        db_tag = await self.get_tag_by_id(tag_id)
        if not db_tag:
            return None
        db_tag.name = tag.name
        await self.session.commit()
        await self.session.refresh(db_tag)
        return db_tag
        
    async def delete_tag(self, tag_id: int) -> bool:
        db_tag = await self.get_tag_by_id(tag_id)
        if not db_tag:
            return False
        await self.session.delete(db_tag)
        await self.session.commit()
        return True
    
    

    
    
    
    
        