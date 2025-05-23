

from typing import Generic, TypeVar

from pydantic import BaseModel

from redis_client.utils import hgetall, hset


T = TypeVar(name="T", bound=BaseModel)

class JobStore(Generic[T]):
    async def save_job(self, name: str, data: T) -> None:
        await hset(name=name, data=data.model_dump())
    
    async def get_job(self, name: str) -> T:
        await hgetall(name=name, return_model=T)
        
    

