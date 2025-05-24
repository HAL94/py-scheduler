import asyncio
from datetime import datetime
from typing import Sequence
import redis.asyncio as redis

from jobs.redis_job_store import RedisJobStore
from utils import sub_two_dates

from .base_queue import BaseQueue
from redis_client import redis_client
from redis_client.utils import get_zrange_item, hgetall
from schema import Job, ZRangeItem


class RedisQueue(BaseQueue[Job]):
    def __init__(self, redis_client: redis.Redis, name="job_queue"):
        self.client = redis_client
        self.name = name
        self.storage = RedisJobStore(client=self.client)        

    async def _save_job_details(self, task: Job):
        await self.storage.save_job(name=task.id, data=task)

    async def _add_scheduled_task(self, task: Job):
        key = f"{self.name}:scheduled:{task.id}"
        await self.storage.save_job(name=key, data=task)

        await self.client.expire(
            name=key,
            time=sub_two_dates(datetime.now(), task.scheduled_at),
        )

    def listen_for_expired_jobs(
        self,
    ):
        pubsub = self.client.pubsub()

        async def run_task():
            await pubsub.psubscribe("__keyevent@0__:expired")
            async for message in pubsub.listen():
                if message and message["type"] == "pmessage":
                    expired_key = message["data"].decode("utf-8")
                    job = await self.storage.get_job(expired_key.split(':')[2])
                    # print(f"job is expired: {job}")
                    if job is not None:
                        key = job.id
                        score = job.priority                        
                        await self.client.zadd(self.name, { key: score })

        listener = asyncio.create_task(run_task())
        
        return listener

    async def add_task(self, task: Job) -> None:
        score = task.priority
        key = task.id

        print(f"Adding job with id: {key} and score is: {score}")

        if datetime.now() < task.scheduled_at:
            await self._add_scheduled_task(task)
        else:
            # add it now to active queue
            await self.client.zadd(self.name, {key: score})

        # always save job regardless it will run now or later
        await self._save_job_details(task)

    async def peek_task(self) -> Job | None:
        next_priority_job = await self.client.zrevrange(
            self.name, start=0, end=0, withscores=True
        )

        if len(next_priority_job) == 0:
            return None

        zitem: ZRangeItem = get_zrange_item(next_priority_job[0])

        fetched_job: Job = await self.storage.get_job(name=zitem.key)

        if not fetched_job:
            return None

        return fetched_job

    async def pop_task(self) -> Job | None:
        priority_job: list[tuple[str, int]] = await self.client.zpopmax(name=self.name)

        if priority_job is None or len(priority_job) <= 0:  # Queue is empty
            return None

        zitem: ZRangeItem = get_zrange_item(priority_job[0])

        fetched_job: Job = await self.storage.get_job(name=zitem.key)

        if not fetched_job:
            return None

        return fetched_job

    async def wait_for_next_task(self, timeout=0) -> Job | None:
        priority_job = await self.client.bzpopmax(keys=self.name, timeout=timeout)

        if not priority_job:
            return None

        _, member, _ = priority_job

        id = member.decode()

        fetched_job: Job = await self.storage.get_job(name=id)
        
        if not fetched_job:
            return None

        fetched_job.id = id


        return fetched_job

    async def list_jobs(self, start=0, end=-1, withscores=True) -> Sequence[Job]:
        data = await self.client.zrevrange(
            self.name, start=start, end=end, withscores=withscores
        )

        jobs_list = []

        for item in data:
            zitem: ZRangeItem = get_zrange_item(item)
            job = await hgetall(zitem.key, Job)
            if job is not None:
                jobs_list.append(job)

        return jobs_list


jobs_queue = RedisQueue(redis_client=redis_client)
