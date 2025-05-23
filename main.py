import asyncio
import random

from app_jobs.job_watch import JobWatch
from app_jobs.job_worker import JobWorker
from app_queue.redis_queue import jobs_queue
from schema import Job


async def main():
    first_job = Job(
        priority=1,
        max_retry_attempts=3,
        retry=True,
        task_name="SendEmail",
        args=["hello", "world"],
        kwargs={"email": "james.brown@gmail.com"},
    )
    print(f"job is {first_job}")
    
    await jobs_queue.add_task(first_job)

    watcher = JobWatch(queue=jobs_queue)

    async def send_email_task_dummy(*args, **kwargs):
        print(f"Send email task: args: {args}, kwargs: {kwargs}")
        random_chance = random.random()
        await asyncio.sleep(5)

        if random_chance < 0.8:
            raise RuntimeError("Failed to send email")

        print("Email is sent")

    worker = JobWorker(processor=send_email_task_dummy)

    await watcher.start(worker=worker)


if __name__ == "__main__":
    asyncio.run(main())
