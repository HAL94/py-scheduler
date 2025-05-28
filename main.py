import asyncio
from datetime import datetime, timedelta
import random


from jobs.job_watch import JobWatch
from jobs.job_worker import JobWorker
from app_queue.redis_queue import jobs_queue
from schema import Job


def schedule_after(seconds=10):
    return datetime.now() + timedelta(seconds=seconds)


async def main():
    job1 = Job(
        id=None,
        priority=5,  # highest value, highest priority
        max_retry_attempts=3,
        scheduled_at=schedule_after(seconds=10),
        task_name="SendEmailDelayed",
        args=["hello", "1st delayed"],
        kwargs={"email": "job1delayed@notification.com"},
    )

    job2 = Job(
        id=None,
        priority=2,
        max_retry_attempts=2,
        task_name="SendEmail",
        args=["Hello", "2nd job"],
        kwargs={"email": "job2@notification.com"},
    )

    job3 = Job(
        id=None,
        priority=3,
        max_retry_attempts=3,
        task_name="SendEmail",
        args=["Hello", "3rd job"],
        kwargs={"email": "job3@notification.com"},
    )
    
    job4 = Job(
        id=None,
        priority=4,
        max_retry_attempts=3,
        task_name="SendEmail",
        args=["Hello", "4rd job"],
        kwargs={"email": "job4@notification.com"},
    )
    
    job5 = Job(
        id=None,
        priority=4,
        max_retry_attempts=3,
        task_name="SendEmail",
        args=["Hello", "5rd job"],
        kwargs={"email": "job5@notification.com"},
    )

    jobs_queue.listen_for_expired_jobs()

    await jobs_queue.add_job(job1)
    await jobs_queue.add_job(job2)
    await jobs_queue.add_job(job3)
    await jobs_queue.add_job(job4)
    await jobs_queue.add_job(job5)
    
    # await asyncio.sleep(10)
    

    # let's see the console for which job will be popped first
    watcher = JobWatch(queue=jobs_queue)

    # dummy task
    async def send_email_task_dummy(*args, **kwargs):
        print(f"Send email task: args: {args}, kwargs: {kwargs}")
        random_chance = random.random()
        await asyncio.sleep(5)

        if random_chance < 0.8:
            raise RuntimeError("Failed to send email")

        print("Email is sent")

    worker = JobWorker(processor=send_email_task_dummy)

    await watcher.start(worker=worker, number_of_workers=2)


if __name__ == "__main__":
    asyncio.run(main())
