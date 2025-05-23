from typing import Sequence
import redis.asyncio as redis

from app_queue.base_queue import BaseQueue
from redis_client import redis_client
from redis_client.utils import get_zrange_item
from schema import Job, ZRangeItem


class JobQueue(BaseQueue[Job]):
    def __init__(self, redis_client: redis.Redis, name = "job_queue"):
        self.client = redis_client
        self.name = name

    
    async def add_task(self, task: Job):
        score = task.priority
        key = task.id
        
        print(f"Adding job with id: {key} and score is: {score}")
        
        await self.client.zadd(self.name, { key: score })
        
    async def peek_task(self) -> ZRangeItem | None:
        next_priority_job = await self.client.zrevrange(self.name, start=0, end=0, withscores=True)
        
        if len(next_priority_job) == 0:
            return None
        
        return get_zrange_item(next_priority_job[0])
    
    async def pop_next_job(self) -> ZRangeItem | None:
        removed_priority_job: tuple[str, int] = await self.client.zpopmax(name=self.name)
        
        if removed_priority_job is None: # Queue is empty
            return None
        
        return get_zrange_item(removed_priority_job)

    async def list_jobs(self, start=0, end=0, withscores=True) -> Sequence[ZRangeItem]:
        data = await self.client.zrevrange(self.name, start=start, end=end, withscores=withscores)
        
        jobs_list = []
        
        for item in data:
            jobs_list.append(get_zrange_item(item))
            
        return jobs_list
    
jobs_queue = JobQueue(redis_client=redis_client)
        
        
        
        