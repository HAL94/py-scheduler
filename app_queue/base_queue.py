

import abc
from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseQueue(abc.ABC, Generic[T]):
    """
    An abstract base class for a queue.
    """
    
    @abc.abstractmethod
    async def add_job(self, task: T) -> None:
        """
        Adds a new job to the queue.

        Args:
            task: The task object to add.
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    async def peek_job(self) -> T:
        """
        View the next task in the queue, without removing it        
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    async def pop_job(self) -> T:
        """
        Pop the next task in the queue, it will be removed
        """
        raise NotImplementedError
    
    async def wait_for_next_job(self, timeout = 0) -> T | None:
        """
        Listen for the jobs queue, and fetch next priority job if available
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    async def list_jobs(self, *args, **kwargs) -> Sequence[T]:
        """
        See all the tasks in the queue
        """
        raise NotImplementedError
    
    
    
