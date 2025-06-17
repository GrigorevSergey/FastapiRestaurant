from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.models.user import User
from src.core.dependencies import get_current_user, get_current_admin_user, get_user_repository
from src.infrastructure.repositories.user import UserRepository
from pydantic import BaseModel, ConfigDict
from typing import Annotated
from fastapi_limiter.depends import RateLimiter

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    number_phone: str
    is_admin: bool
    is_active: bool

router = APIRouter(prefix="/users", tags=["users"])



@router.get("/", response_model=UserResponse,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_users(
    current_user: Annotated[User, Depends(get_current_user)]
) -> UserResponse:
    return UserResponse.model_validate(current_user)

@router.put("/", response_model=UserResponse,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_user(
    user_update: dict,
    current_user: Annotated[User, Depends(get_current_user)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserResponse:
    updated_user = await user_repository.update(current_user.id, user_update)
    return UserResponse.model_validate(updated_user)

@router.get("/{user_id}", response_model=UserResponse,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_user(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserResponse:
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return UserResponse.model_validate(user) 