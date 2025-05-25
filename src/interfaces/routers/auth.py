# src/interfaces/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.schemas.user_schemas import PhoneRequest, VerifyRequest, TokenResponse, CreateSuperUserRequest, LoginRequest
from src.infrastructure.services.sms import SMSService
from src.infrastructure.repositories.user import UserRepository
from src.application.auth.auth import AuthService
from src.core.security import create_access_token, verify_password
from src.core.config import settings
from datetime import timedelta
from src.infrastructure.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

sms_service = SMSService()

@router.post("/register", status_code=status.HTTP_200_OK)
async def request_sms_code(
    data: PhoneRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AuthService(UserRepository(db), sms_service)
        await service.verification(data.number_phone)
        return {"message": "Код отправлен"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Ошибка при регистрации: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.post("/confirm", response_model=TokenResponse)
async def verify_sms_code(
    data: VerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AuthService(UserRepository(db), sms_service)
        user = await service.verification_user(data.number_phone, data.code)
        if not user:
            raise HTTPException(status_code=400, detail="Неверный код подтверждения")
        token = create_access_token({"sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Ошибка при подтверждении кода: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.post("/create-superuser", status_code=status.HTTP_201_CREATED)
async def create_superuser(
    data: CreateSuperUserRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AuthService(UserRepository(db), sms_service)
        user = await service.create_superuser(data.number_phone, data.admin_password)
        return {"message": f"Superuser {user.number_phone} created"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Ошибка при создании суперпользователя: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        user_repository = UserRepository(db)
        user = await user_repository.get_by_phone(login_data.number_phone)
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный номер телефона или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"Ошибка при входе: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")