# src/interfaces/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.schemas.user_schemas import PhoneRequest, VerifyRequest, TokenResponse, CreateSuperUserRequest
from src.infrastructure.services.sms import SMSService
from src.infrastructure.repositories.user import UserRepository
from src.application.auth.auth import AuthService
from src.core.security import create_access_token

router = APIRouter(tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_200_OK)
async def request_sms_code(
    data: PhoneRequest, db: AsyncSession = Depends(get_db),sms_service: SMSService = Depends()):
    try:
        service = AuthService(UserRepository(db), sms_service)
        await service.verification(data.number_phone)
        return {"message": "Код отправлен"}
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@router.post("/confirm", response_model=TokenResponse)
async def verify_sms_code(data: VerifyRequest,db: AsyncSession = Depends(get_db),
    sms_service: SMSService = Depends()):
    try:
        service = AuthService(UserRepository(db), sms_service)
        user = await service.verification_user(data.number_phone, data.code)
        token = create_access_token(user.number_phone)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@router.post("/create-superuser", status_code=status.HTTP_201_CREATED)
async def create_superuser(data: CreateSuperUserRequest,db: AsyncSession = Depends(get_db)):
    try:
        service = AuthService(UserRepository(db), SMSService())
        user = await service.create_superuser(data.number_phone, data.admin_password)
        return {"message": f"Superuser {user.number_phone} created"}
    except Exception as e:
        raise HTTPException(400, detail=str(e))