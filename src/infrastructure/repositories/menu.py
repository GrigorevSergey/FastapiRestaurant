from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.infrastructure.models.menu import Category, Dish, Tag, ComboSet
from src.domain.menu import CategoryCreate, DishCreate, CategoryUpdate, DishUpdate, TagCreate, TagUpdate, ComboSetCreate, ComboSetUpdate
from src.redis import cache, invalidate_cache


class MenuRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    @cache()
    async def get_categories(self, limit: int = 10, offset: int = 0) -> list[Category]:
        result = await self.session.execute(
            select(Category).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def create_category(self, category: CategoryCreate) -> Category:
        db_category = Category(
            name=category.name,
            description=category.description
        )
        self.session.add(db_category)
        await self.session.commit()
        await self.session.refresh(db_category)
        await invalidate_cache("get_category_id*")
        return db_category
    
    async def update_category(self, category_id: int, category: CategoryUpdate) -> Category | None:
        db_category = await self.get_category_id(category_id)
        if not db_category:
            return None
        db_category.name = category.name
        db_category.description = category.description
        await self.session.commit()
        await self.session.refresh(db_category)
        await invalidate_cache(f"get_category_id*{category_id}*")
        await invalidate_cache("get_category_id*")
        return db_category
    
    async def get_category_id(self, category_id: int) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
    
    async def delete_category(self, category_id: int) -> bool:  
        db_category = await self.get_category_id(category_id)
        if not db_category:
            return False
        await self.session.delete(db_category)
        await self.session.commit()
        await invalidate_cache("get_categories*")
        await invalidate_cache(f"get_category_id*{category_id}*")
        return True

    @cache()
    async def get_dishes(self, limit: int = 10, offset: int = 0) -> list[Dish]:
        result = await self.session.execute(
            select(Dish).limit(limit).offset(offset)
        )
        return result.scalars().all()
    
    @cache()
    async def get_dish_id(self, dish_id: int) -> Dish | None:
        result = await self.session.execute(
            select(Dish).where(Dish.id == dish_id)
        )
        return result.scalar_one_or_none()
    
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
        await invalidate_cache("get_dishes*")
        await invalidate_cache(f"get_dish_id*{db_dish.id}*")
        return db_dish
    
    async def update_dish(self, dish_id: int, dish: DishUpdate) -> Dish | None:
        db_dish = await self.get_dish_id(dish_id)
        if not db_dish:
            return None
        db_dish.name = dish.name
        db_dish.description = dish.description
        db_dish.price = dish.price
        db_dish.category_id = dish.category_id
        await self.session.commit()
        await self.session.refresh(db_dish)
        await invalidate_cache("get_dishes*")
        await invalidate_cache(f"get_dish_id*{dish_id}*")
        return db_dish
    
    async def delete_dish(self, dish_id: int) -> bool:
        db_dish = await self.get_dish_id(dish_id)
        if not db_dish:
            return False
        await self.session.delete(db_dish)
        await self.session.commit()
        await invalidate_cache("get_dishes*")
        await invalidate_cache(f"get_dish_id*{dish_id}*")
        await invalidate_cache("get_dish_id*")
        return True
    
    @cache()
    async def get_dishes_category_id(self, category_id: int) -> list[Dish]:
        result = await self.session.execute(
            select(Dish).where(Dish.category_id == category_id)
        )
        await invalidate_cache(f"get_dishes_category_id*{category_id}*")
        return result.scalars().all()
    
    @cache()
    async def get_tags(self, limit: int = 10, offset: int = 0) -> list[Tag]:
        result = await self.session.execute(
            select(Tag).limit(limit).offset(offset)
        )
        await invalidate_cache("get_tags*")
        return result.scalars().all()
    
    @cache()
    async def get_tag_id(self, tag_id: int) -> Tag | None:
        result = await self.session.execute(
            select(Tag).where(Tag.id == tag_id)
        )
        await invalidate_cache(f"get_tag_id*{tag_id}*")
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
        await invalidate_cache("get_tags*")
        await invalidate_cache(f"get_tag_id*{db_tag.id}*")
        await invalidate_cache("get_tag_id*")
        return db_tag
    
    async def update_tag(self, tag_id: int, tag: TagUpdate) -> Tag | None:  
        db_tag = await self.get_tag_id(tag_id)
        if not db_tag:
            return None
        db_tag.name = tag.name
        await self.session.commit()
        await self.session.refresh(db_tag)
        await invalidate_cache("get_tags*")
        await invalidate_cache(f"get_tag_id*{tag_id}*")
        await invalidate_cache("get_tag_id*")
        return db_tag
        
    async def delete_tag(self, tag_id: int) -> bool:
        db_tag = await self.get_tag_id(tag_id)
        if not db_tag:
            return False
        await self.session.delete(db_tag)
        await self.session.commit()
        await invalidate_cache("get_tags*")
        await invalidate_cache(f"get_tag_id*{tag_id}*")
        await invalidate_cache("get_tag_id*")
        return True
    
    async def create_combo(self, combo: ComboSetCreate) -> ComboSet:
        db_combo = ComboSet(name=combo.name, description=combo.description, price=combo.price)
        if hasattr(combo, 'dish_ids') and combo.dish_ids:
            for dish_id in combo.dish_ids:
                dish = await self.get_dish_id(dish_id)
                if dish:
                    db_combo.dishes.append(dish)
        self.session.add(db_combo)
        await self.session.commit()
        await self.session.refresh(db_combo)
        await invalidate_cache("get_combos*")
        await invalidate_cache(f"get_combo_id*{db_combo.id}*")
        await invalidate_cache("get_combo_id*")
        return db_combo

    async def update_combo(self, combo_id: int, combo: ComboSetUpdate) -> ComboSet | None:
        result = await self.session.execute(
            select(ComboSet).options(selectinload(ComboSet.dishes)).where(ComboSet.id == combo_id)
        )
        db_combo = result.scalar_one_or_none()
        if not db_combo:
            return None
            
        if combo.name is not None:
            db_combo.name = combo.name
        if combo.description is not None:
            db_combo.description = combo.description
        if combo.price is not None:
            db_combo.price = combo.price
            
        if combo.dish_ids is not None:
            dishes_query = select(Dish).where(Dish.id.in_(combo.dish_ids))
            dishes_result = await self.session.execute(dishes_query)
            new_dishes = dishes_result.scalars().all()
            
            db_combo.dishes = new_dishes
            
        await self.session.commit()
        await self.session.refresh(db_combo, ["dishes"])
        await invalidate_cache("get_combos*")
        await invalidate_cache(f"get_combo_id*{combo_id}*")
        return db_combo

    @cache()
    async def get_combo_id(self, combo_id: int) -> ComboSet | None:
        result = await self.session.execute(
            select(ComboSet).where(ComboSet.id == combo_id)
        )
        await invalidate_cache(f"get_combo_id*{combo_id}*")
        await invalidate_cache("get_combo_id*")
        return result.scalar_one_or_none()

    @cache()
    async def get_combos(self, limit: int = 10, offset: int = 0) -> list[ComboSet]:
        result = await self.session.execute(
            select(ComboSet).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def delete_combo(self, combo_id: int) -> bool:
        db_combo = await self.get_combo_id(combo_id)
        if not db_combo:
            return False
        await self.session.delete(db_combo)
        await self.session.commit()
        await invalidate_cache("get_combos*")
        await invalidate_cache(f"get_combo_id*{combo_id}*")
        await invalidate_cache("get_combo_id*")
        return True
    
    

    
    
    
    
        