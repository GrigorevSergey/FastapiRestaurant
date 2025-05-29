from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.models.user import User
from src.core.dependencies import get_current_user, get_current_admin_user, get_user_repository
from src.infrastructure.repositories.user import UserRepository
from pydantic import BaseModel
from typing import Annotated

class UserResponse(BaseModel):
    id: str
    number_phone: str
    is_admin: bool
    is_active: bool

    class Config:
        from_attributes = True

router = APIRouter(prefix="/users", tags=["users"])



@router.get("/", response_model=UserResponse)
async def read_users(
    current_user: Annotated[User, Depends(get_current_user)]
) -> UserResponse:
    return UserResponse.model_validate(current_user)

@router.put("/", response_model=UserResponse)
async def update_user(
    user_update: dict,
    current_user: Annotated[User, Depends(get_current_user)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserResponse:
    updated_user = await user_repository.update(current_user.id, user_update)
    return UserResponse.model_validate(updated_user)

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserResponse:
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return UserResponse.model_validate(user) 