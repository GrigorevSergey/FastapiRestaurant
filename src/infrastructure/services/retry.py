from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx
from httpx import TimeoutException, HTTPStatusError
import logging
logger = logging.getLogger(__name__)


class RetryService:
    @retry(stop=stop_after_attempt(300), 
           wait=wait_exponential(multiplier=1, min=2, max=30),
           retry=retry_if_exception_type((TimeoutException, HTTPStatusError)),
           before_sleep=before_sleep_log(logger, logging.INFO)
           )
    async def get(self, url, headers=None):
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    
    @retry(stop=stop_after_attempt(3), 
           wait=wait_exponential(multiplier=1, min=1, max=10),
           retry=retry_if_exception_type((TimeoutException, HTTPStatusError)),
           before_sleep=before_sleep_log(logger, logging.INFO)
           )
    async def post(self, url, headers=None, json=None):
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=json)
            response.raise_for_status()
            return response.json()
        
    async def check_health(self, url, headers=None):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health")
                return response.status_code == 200
        except (TimeoutException, HTTPStatusError):
            return False
        
        
        
        