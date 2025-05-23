import asyncio
from typing import Any, Awaitable, Callable


async def delayed_task(delay_seconds: int, func: Callable[[Any], Awaitable[Any]]):
    """
    An asynchronous function that simulates a task taking a certain amount of time.

    Args:
        delay_seconds: The number of seconds to wait before the task "resolves".
    """
    await asyncio.sleep(delay_seconds)
    if func is not None:
        await func()
    
    