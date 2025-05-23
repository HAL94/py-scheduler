from typing import Sequence
import redis.asyncio as redis

from redis_client import redis_client
from redis_client.utils import get_zrange_item
from schema import Job, ZRangeItem

# self.client.zadd(self.channel, {key: score})
# self.client.hset(name=key, mapping=player_info)

# dt_suffix = entry.date
# dt_key = f"{key}:{dt_suffix}"

# key = f"{ALL_GAMES}:{user_id}:{self.channel}"
# self.client.zadd(ALL_GAMES, mapping={key: score})
# self.client.hset(name=key, mapping=player_info)
# self.client.hset(name=dt_key, mapping=player_info)

# channel_by_date = f"lb:{entry.date}"
# self.client.zadd(channel_by_date, {dt_key: score})

class JobQueue():
    def __init__(self, redis_client: redis.Redis, name = "job_queue"):
        self.client = redis_client
        self.name = name

    
    async def add_task(self, task: Job):
        score = task.priority
        key = str(task.id)
        
        print(f"Adding job with id: {key} and score is: {score}")
        
        await self.client.zadd(self.name, { key: score })
        
    async def get_next_task(self) -> ZRangeItem:
        next_priority_job = await self.client.zrevrange(self.name, start=0, end=0, withscores=True)
        
        return get_zrange_item(next_priority_job[0])
    
    async def pop_next_job(self) -> ZRangeItem:
        removed_priority_job: tuple[str, int] = await self.client.zpopmax(name=self.name)
        
        return get_zrange_item(removed_priority_job)

    async def list_jobs(self, start=0, end=0, withscores=True) -> Sequence[ZRangeItem]:
        
            
        data = await self.client.zrevrange(self.name, start=start, end=end, withscores=withscores)
        
        jobs_list = []
        
        for item in data:
            jobs_list.append(get_zrange_item(item))
            
        return jobs_list
    
jobs_queue = JobQueue(redis_client=redis_client)
        
        
        
        