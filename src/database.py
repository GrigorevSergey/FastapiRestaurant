from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.core.config import settings
from sqlalchemy.pool import NullPool
import os


Base = declarative_base()

DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA", "public")

engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"server_settings": {"search_path": DATABASE_SCHEMA}}
)

async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except Exception as ex:
            await session.rollback()
            raise ex
        finally:
            await session.close()
            
            


