import abc
from typing import ClassVar, Generic, TypeVar
import redis.asyncio as redis
from pydantic import BaseModel

T = TypeVar(name="T", bound=BaseModel)


class BaseJobStore(abc.ABC, Generic[T]):
    __model__: ClassVar[T]

    def __init__(self, client: redis.Redis):
        self.client = client

    @property
    def _model(self) -> T:
        return self.__model__

    @abc.abstractmethod
    async def save_job(self, name: str, data: T) -> None:
        raise NotImplementedError
        

    @abc.abstractmethod
    async def get_job(self, name: str) -> T | None:
        raise NotImplementedError

