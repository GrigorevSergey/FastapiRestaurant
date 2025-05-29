from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.infrastructure.repositories.menu import MenuRepository
from pydantic import BaseModel, Field


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
    category = await MenuRepository(db).get_category(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return CategoryResponse.model_validate(category)

@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category: CategoryResponse,
    db: AsyncSession = Depends(get_db)
):
    new_category = await MenuRepository(db).create_category(category)
    return CategoryResponse.model_validate(new_category)

@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category: CategoryResponse,
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
    dishes = await MenuRepository(db).get_dishes_category(category_id)
    if not dishes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No dishes found for this category"
        )
    return dishes

@router.post("/dishes", response_model=DishResponse)
async def create_dish(
    dish: DishResponse,
    db: AsyncSession = Depends(get_db)
):
    new_dish = await MenuRepository(db).create_dish(dish)
    return DishResponse.model_validate(new_dish)

@router.put("/dishes/{dish_id}", response_model=DishResponse)
async def update_dish(
    dish_id: int,
    dish: DishResponse,
    db: AsyncSession = Depends(get_db)
):
    updated_dish = await MenuRepository(db).update_dish(dish_id, dish)
    if not updated_dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )
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
    tag = await MenuRepository(db).get_tag(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return TagResponse.model_validate(tag)

@router.post("/tags", response_model=TagResponse)
async def create_tag(
    tag: TagResponse,
    db: AsyncSession = Depends(get_db)
):
    new_tag = await MenuRepository(db).create_tag(tag)
    return TagResponse.model_validate(new_tag)

@router.put("/tags/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag: TagResponse,
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



