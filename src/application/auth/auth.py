from src.domain.user import User, UserCreate
from src.core.security import get_password_hash, verify_password
from src.core.config import settings
from src.infrastructure.repositories.user import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository, sms_service):
        self.user_repository = user_repository
        self.sms_service = sms_service
        self.admin_password_hash = get_password_hash(settings.SUPERUSER_PASSWORD)
        
    async def verification(self, number_phone: str):
        if await self.user_repository.get_by_phone(number_phone):  
            raise ValueError("User already exists")
        self.sms_service.send_sms(number_phone)
        
    async def verification_user(self, number_phone: str, code: str) -> User:
        if not self.sms_service.verify_code(number_phone, str(code)):  
            raise ValueError("Invalid code")
    
        user = await self.user_repository.get_by_phone(number_phone)
        if not user:
            new_user = UserCreate(
                number_phone=number_phone,
                password="",  
                is_phone_verified=True
            )
            return await self.user_repository.create(new_user)
        return user

    async def create_superuser(self, number_phone: str, password: str): 
        if not verify_password(password, self.admin_password_hash):
            raise ValueError("Invalid admin password")
        
        user = await self.user_repository.get_by_phone(number_phone)
        if not user:
            raise ValueError("User not found")
        
        return await self.user_repository.make_admin(number_phone)

    async def register(self, number_phone: str, password: str) -> User:
        if await self.user_repository.get_by_phone(number_phone): 
            raise ValueError("Пользователь с таким номером телефона уже существует")

        user = UserCreate(
            number_phone=number_phone,
            password=password
        )
        return await self.user_repository.create(user)

    async def login(self, number_phone: str, password: str) -> User:
        user = await self.user_repository.get_by_phone(number_phone) 
        if not user:
            raise ValueError("Пользователь не найден")

        if user.hashed_password != password: 
            raise ValueError("Неверный пароль")

        return user

    async def verify_phone(self, number_phone: str, code: str) -> User:
        user = await self.user_repository.get_by_phone(number_phone) 
        if not user:
            raise ValueError("Пользователь не найден")

        user.is_phone_verified = True
        await self.user_repository.update(user.id, user)

        return user