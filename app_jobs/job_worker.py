

from typing import Awaitable, Callable, Generic, TypeVar

T = TypeVar(name="T")

class JobWorker(Generic[T]):
    def __init__(self, processor: Callable[[T], Awaitable[None]]):
        self.processor = processor
        # consider configuring multiple workers
        # number_of_workers = 1
    
    