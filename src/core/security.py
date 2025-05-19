import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from src.core.config import settings


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def create_access_token(phone: str) -> str:
    payload = {
        "sub": phone, 
        "exp": datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.PyJWTError:
        return None
    
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)