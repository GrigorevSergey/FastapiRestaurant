from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase


from src.core.config import settings


engine = create_async_engine(
    settings.DATABASE_URL, 
    future=True,  
    echo=True 
)

AsyncSessionLocal = sessionmaker(
    bind=engine,  
    class_=AsyncSession,  
    expire_on_commit=True, 
    autoflush=False 
)

class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:  
        try:
            yield session  
        except:
            await session.rollback()
            raise
        finally:
            await session.close()