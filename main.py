import asyncio
from datetime import datetime, timedelta
import random


from jobs.job_watch import JobWatch
from jobs.job_worker import JobWorker
from app_queue.redis_queue import jobs_queue
from schema import Job


def add_job(job: Job):
    print(f"job is {job}")
    if job.scheduled_at is not None and datetime.now() >= job.scheduled_at:
        print("Should add the task now")
    else:
        print(f"Should add to a scheduled hash with expiry at: {job.scheduled_at}")

async def main():
    first_job = Job(
        id=None,
        priority=1,
        max_retry_attempts=3,
        scheduled_at=datetime.now() + timedelta(seconds=10),
        retry=True,
        task_name="SendEmail",
        args=["hello", "world"],
        kwargs={"email": "james.brown@gmail.com"},
    )
    add_job(job=first_job)    
    
    jobs_queue.listen_for_expired_jobs()

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
