import asyncio

from job_queue import jobs_queue
from redis_client.utils import hgetall, hset
from schema import Job

async def main():
    first_job = Job(priority=1, max_retry_attempts=3, retry=True)
    second_job = Job(priority=0, max_retry_attempts=1, retry=True)
    third_job = Job(priority=2, max_retry_attempts=3, retry=True)
    
    await jobs_queue.add_task(first_job)
    
    await hset(first_job.id, first_job.model_dump())
    await hset(second_job.id, second_job.model_dump())
    await hset(third_job.id, third_job.model_dump())
    
    await jobs_queue.add_task(second_job)
    await jobs_queue.add_task(third_job)
    
    print("Hello from py-scheduler!")
    
    print("Here are your jobs:")
    jobs = await jobs_queue.list_jobs(start=0, end=-1, withscores=True)
    print(jobs)
    
    print("Next priority job")
    next_job = await jobs_queue.get_next_task()
    print(f"Next job on the queue: {next_job}")
    
    parsed_job = await hgetall(next_job.key, Job)
    
    print(f"parsed_job: {parsed_job}")
    
    
    


if __name__ == "__main__":
    asyncio.run(main())
