from pydantic import BaseModel


class PhoneRequest(BaseModel):
        number_phone: str


class VerifyRequest(PhoneRequest):
    code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CreateSuperUserRequest(BaseModel):
    number_phone: str
    admin_password: str