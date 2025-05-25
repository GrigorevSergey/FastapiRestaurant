from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.infrastructure.models.user import User
from src.domain.user import UserCreate, UserUpdate, UserInDB
from src.core.security import get_password_hash

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: UserCreate) -> User:
        db_user = User(
            name=user.name,
            email=user.email,
            number_phone=user.number_phone,
            hashed_password=get_password_hash(user.password),
            is_admin=user.is_admin,
            is_phone_verified=user.is_phone_verified
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def get_by_phone(self, phone: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.number_phone == phone)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def update(self, user_id: int, user_update: UserUpdate) -> User | None:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "password":
                setattr(db_user, "hashed_password", value) 
            else:
                setattr(db_user, field, value)

        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def make_admin(self, phone: str) -> User:
        user = await self.get_by_phone(phone)
        if not user:
            raise ValueError("Пользователь не найден")
        
        user.is_admin = True
        await self.session.commit()
        await self.session.refresh(user)
        return user