from redis.asyncio import Redis
from functools import wraps
import json
from src.core.config import settings

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

async def get_redis() -> Redis:
    return redis_client

async def close_redis():
    await redis_client.close()

def cache(expire: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            
            if cached := await redis_client.get(key):
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            
            await redis_client.set(key, json.dumps(result, default=str), ex=expire)
            return result 
        return wrapper
    return decorator


async def invalidate_cache(pattern: str):
    keys = await redis_client.keys(pattern)
    if keys: await redis_client.delete(*keys)