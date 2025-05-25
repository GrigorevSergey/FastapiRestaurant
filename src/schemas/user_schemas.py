from pydantic import BaseModel, field_validator
import re

class PhoneRequest(BaseModel):
    number_phone: str
    
    @field_validator("number_phone")
    def validate_number_phone(cls, value: str) -> str:
        pattern = r"^\+7[0-9]{10}$"
        if not re.match(pattern, value):
            raise ValueError("Неверный формат номера телефона")
        return value

class VerifyRequest(PhoneRequest):
    code: str
    
    @field_validator("code")
    def validate_code(cls, value: str) -> str:
        if not value.isdigit() or len(value) != 4:
            raise ValueError("Неверное количество цифр в коде")
        return value


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CreateSuperUserRequest(PhoneRequest):
    admin_password: str
    
    @field_validator("admin_password")
    def validate_admin_password(cls, value: str) -> str:
        if len(value) < 4:
            raise ValueError("Пароль должен содержать минимум 4 символа")
        return value
    
    
class LoginRequest(BaseModel):
    number_phone: str
    password: str