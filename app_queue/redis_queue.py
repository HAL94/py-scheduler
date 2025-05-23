from typing import Sequence
import redis.asyncio as redis

from .base_queue import BaseQueue
from redis_client import redis_client
from redis_client.utils import get_zrange_item, hgetall
from schema import Job, ZRangeItem


class RedisQueue(BaseQueue[Job]):
    def __init__(self, redis_client: redis.Redis, name = "job_queue"):
        self.client = redis_client
        self.name = name
    
    async def add_task(self, task: Job) -> None:
        score = task.priority
        key = task.id
        
        print(f"Adding job with id: {key} and score is: {score}")
        
        await self.client.zadd(self.name, { key: score })
        
    async def peek_task(self) -> Job | None:
        next_priority_job = await self.client.zrevrange(self.name, start=0, end=0, withscores=True)
        
        if len(next_priority_job) == 0:
            return None
        
        zitem: ZRangeItem = get_zrange_item(next_priority_job[0])
        
        fetched_job: Job = await hgetall(zitem.key, Job)
        
        if not fetched_job:
            return None
        
        return fetched_job
        
    
    async def pop_task(self) -> Job | None:
        priority_job: list[tuple[str, int]] = await self.client.zpopmax(name=self.name)
                
        if priority_job is None or len(priority_job) <= 0: # Queue is empty
            return None
        
        zitem: ZRangeItem = get_zrange_item(priority_job[0])
        
        fetched_job: Job = await hgetall(zitem.key, Job)
        
        if not fetched_job:
            return None
        
        return fetched_job
        

    async def list_jobs(self, start=0, end=-1, withscores=True) -> Sequence[Job]:
        data = await self.client.zrevrange(self.name, start=start, end=end, withscores=withscores)
        
        jobs_list = []
        
        for item in data:
            zitem: ZRangeItem = get_zrange_item(item)
            job = await hgetall(zitem.key, Job)
            if job is not None:
                jobs_list.append(job)
            
        return jobs_list
    
jobs_queue = RedisQueue(redis_client=redis_client)
        
        
        
        