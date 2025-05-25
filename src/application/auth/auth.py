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
        try:
            if await self.user_repository.get_by_phone(number_phone):  
                raise ValueError("Пользователь с таким номером телефона уже существует")
            await self.sms_service.send_sms(number_phone)
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Ошибка при верификации: {str(e)}")
            raise ValueError("Ошибка при отправке SMS")
        
    async def verification_user(self, number_phone: str, code: str) -> User:
        try:
            if not await self.sms_service.verify_code(number_phone, str(code)):  
                raise ValueError("Неверный код подтверждения")
        
            user = await self.user_repository.get_by_phone(number_phone)
            if not user:
                new_user = UserCreate(
                    number_phone=number_phone,
                    password="", 
                    is_phone_verified=True
                )
                return await self.user_repository.create(new_user)
            return user
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Ошибка при подтверждении кода: {str(e)}")
            raise ValueError("Ошибка при подтверждении кода")

    async def create_superuser(self, number_phone: str, password: str): 
        try:
            if not verify_password(password, self.admin_password_hash):
                raise ValueError("Неверный пароль администратора")
            
            user = await self.user_repository.get_by_phone(number_phone)
            if not user:
                raise ValueError("Пользователь не найден")
            
            return await self.user_repository.make_admin(number_phone)
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Ошибка при создании суперпользователя: {str(e)}")
            raise ValueError("Ошибка при создании суперпользователя")

    async def register(self, number_phone: str, password: str) -> User:
        try:
            if await self.user_repository.get_by_phone(number_phone): 
                raise ValueError("Пользователь с таким номером телефона уже существует")

            user = UserCreate(
                number_phone=number_phone,
                hashed_password=get_password_hash(password)
            )
            return await self.user_repository.create(user)
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Ошибка при регистрации: {str(e)}")
            raise ValueError("Ошибка при регистрации пользователя")

    async def login(self, number_phone: str, password: str) -> User:
        try:
            user = await self.user_repository.get_by_phone(number_phone) 
            if not user:
                raise ValueError("Пользователь не найден")

            if not verify_password(password, user.hashed_password): 
                raise ValueError("Неверный пароль")

            return user
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Ошибка при входе: {str(e)}")
            raise ValueError("Ошибка при входе в систему")

    async def verify_phone(self, number_phone: str, code: str) -> User:
        try:
            user = await self.user_repository.get_by_phone(number_phone) 
            if not user:
                raise ValueError("Пользователь не найден")

            if not await self.sms_service.verify_code(number_phone, code):
                raise ValueError("Неверный код подтверждения")

            user.is_phone_verified = True
            await self.user_repository.update(user.id, user)

            return user
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Ошибка при верификации телефона: {str(e)}")
            raise ValueError("Ошибка при верификации телефона")