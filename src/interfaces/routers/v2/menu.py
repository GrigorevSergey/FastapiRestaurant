from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.infrastructure.repositories.menu import MenuRepository
from src.infrastructure.services.menu_events import MenuEventService
from src.infrastructure.services.menu_events_service import menu_event_service
from src.rabbitmq import RabbitMQClient
from pydantic import BaseModel, Field
from src.schemas.menu_schemas import CategoryCreate, CategoryUpdate, DishCreate, DishUpdate, TagCreate, TagUpdate


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str
    
    class Config:
        from_attributes = True

class DishResponse(BaseModel):
    id: int
    name: str
    description: str
    price: int
    category_id: int
    
    class Config:
        from_attributes = True
    
    
class TagResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True
        

class ComboResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    dish_ids: List[int]

    class Config:
        from_attributes = True
        
    
router = APIRouter(prefix="/menu", tags=["v2"])


@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(0, ge=0, description="Сдвиг записей"),
    offset: int = Query(10, ge=0, description="Лимит записей на странице")
):
    categories = await MenuRepository(db).get_categories(offset, limit)
    return categories

@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    category = await MenuRepository(db).get_category_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return CategoryResponse.model_validate(category)

@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    new_category = await MenuRepository(db).create_category(category)
    return CategoryResponse.model_validate(new_category)

@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    updated_category = await MenuRepository(db).update_category(category_id, category)
    if not updated_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return CategoryResponse.model_validate(updated_category)

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted = await MenuRepository(db).delete_category(category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return {"detail": "Category deleted successfully"}



@router.get("/dishes", response_model=list[DishResponse])
async def get_dishes(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(0, ge=0, description="Сдвиг записей"),
    offset: int = Query(10, ge=0, description="Лимит записей на странице")
):
    dishes = await MenuRepository(db).get_dishes(limit, offset)
    return dishes

@router.get("/dishes/{category_id}", response_model=list[DishResponse])
async def get_dishes_by_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    dishes = await MenuRepository(db).get_dishes_category_id(category_id)
    if not dishes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No dishes found for this category"
        )
    return dishes

async def get_menu_event_service() -> MenuEventService:
    if menu_event_service is None:
        raise RuntimeError("Menu event service not initialized")
    return menu_event_service

@router.post("/dishes", response_model=DishResponse)
async def create_dish(
    dish: DishCreate,
    db: AsyncSession = Depends(get_db),
    event_service: MenuEventService = Depends(get_menu_event_service)
):
    new_dish = await MenuRepository(db).create_dish(dish)
    await event_service.publish_dish_created(new_dish)
    return DishResponse.model_validate(new_dish)

@router.put("/dishes/{dish_id}", response_model=DishResponse)
async def update_dish(
    dish_id: int,
    dish: DishUpdate,
    db: AsyncSession = Depends(get_db),
    event_service: MenuEventService = Depends(get_menu_event_service)
):
    old_dish = await MenuRepository(db).get_dish_id(dish_id)
    if not old_dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )
    updated_dish = await MenuRepository(db).update_dish(dish_id, dish)
    if old_dish.price != updated_dish.price:
        await event_service.publish_price_changed(updated_dish, old_dish.price)
    if old_dish.is_available != updated_dish.is_available:
        await event_service.publish_availability_changed(updated_dish, old_dish.is_available)
    return DishResponse.model_validate(updated_dish)

@router.delete("/dishes/{dish_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dish(
    dish_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted = await MenuRepository(db).delete_dish(dish_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )
    return {"detail": "Dish deleted successfully"}

@router.get("/tags", response_model=list[TagResponse])
async def get_tags(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(0, ge=0, description="Сдвиг записей"),
    offset: int = Query(10, ge=0, description="Лимит записей на странице")
):
    tags = await MenuRepository(db).get_tags(limit, offset)
    return tags

@router.get("/tags/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db)
):
    tag = await MenuRepository(db).get_tag_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return TagResponse.model_validate(tag)

@router.post("/tags", response_model=TagResponse)
async def create_tag(
    tag: TagCreate,
    db: AsyncSession = Depends(get_db)
):
    new_tag = await MenuRepository(db).create_tag(tag)
    return TagResponse.model_validate(new_tag)

@router.put("/tags/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag: TagUpdate,
    db: AsyncSession = Depends(get_db)
):
    updated_tag = await MenuRepository(db).update_tag(tag_id, tag)
    if not updated_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return TagResponse.model_validate(updated_tag)

@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted = await MenuRepository(db).delete_tag(tag_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return {"detail": "Tag deleted successfully"}

@router.get("/combo_sets", response_model=list[ComboResponse])
async def get_combos(db: AsyncSession = Depends(get_db)):
    combos = await MenuRepository(db).get_combos()
    result = []
    for combo in combos:
        await db.refresh(combo, ["dishes"])
        result.append(
            ComboResponse(
                id=combo.id,
                name=combo.name,
                description=combo.description,
                price=combo.price,
                dish_ids=[dish.id for dish in combo.dishes]
            )
        )
    return result
    
@router.get("/combo_sets/{combo_id}", response_model=ComboResponse)
async def get_combo(
    combo_id: int,
    db: AsyncSession = Depends(get_db)
):
    combo = await MenuRepository(db).get_combo_id(combo_id)
    if not combo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combo not found"
        )
    await db.refresh(combo, ["dishes"])
    return ComboResponse(
        id=combo.id,
        name=combo.name,
        description=combo.description,
        price=combo.price,
        dish_ids=[dish.id for dish in combo.dishes]
    )

@router.post("/combo_sets", response_model=ComboResponse)
async def create_combo(
    combo: ComboResponse,
    db: AsyncSession = Depends(get_db)
):
    new_combo = await MenuRepository(db).create_combo(combo)
    await db.refresh(new_combo, ["dishes"])
    return ComboResponse(
        id=new_combo.id,
        name=new_combo.name,
        description=new_combo.description,
        price=new_combo.price,
        dish_ids=[dish.id for dish in new_combo.dishes]
    )
    
@router.put("/combo_sets/{combo_id}", response_model=ComboResponse)
async def update_combo(
    combo_id: int,
    combo: ComboResponse,
    db: AsyncSession = Depends(get_db)
):
    updated_combo = await MenuRepository(db).update_combo(combo_id, combo)
    if not updated_combo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combo not found"
        )
    await db.refresh(updated_combo, ["dishes"])
    return ComboResponse(
        id=updated_combo.id,
        name=updated_combo.name,
        description=updated_combo.description,
        price=updated_combo.price,
        dish_ids=[dish.id for dish in updated_combo.dishes]
    )
@router.delete("/combo_sets/{combo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_combo(
    combo_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted = await MenuRepository(db).delete_combo(combo_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combo not found"
        )
    return {"detail": "Combo deleted successfully"}



