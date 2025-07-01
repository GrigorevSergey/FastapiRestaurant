from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from src.core.config import settings
from src.infrastructure.models.user import User
from src.infrastructure.repositories.user import UserRepository
from src.infrastructure.services.menu_events import MenuEventService
from typing import Annotated, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_user_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> AsyncGenerator[UserRepository, None]:
    yield UserRepository(db)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except JWTError:
        raise credentials_exception
    except ValueError:
        raise credentials_exception
    
    user = await user_repository.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_menu_event_service(request: Request) -> MenuEventService:
    service = getattr(request.app.state, "menu_event_service", None)
    if service is None:
        raise RuntimeError("Menu event service not initialized")
    return service