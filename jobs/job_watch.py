import asyncio
from datetime import datetime
from jobs.job_worker import JobWorker
from app_queue.base_queue import BaseQueue
from redis_client.utils import hset
from schema import Job, JobStatus


class JobWatch:
    def __init__(self, queue: BaseQueue[Job]):
        self.queue = queue

    async def _update_job_status(self, job: Job, status: JobStatus):
        if not isinstance(status, JobStatus) or not status:
            return

        job.status = status

        if status == JobStatus.COMPLETED:
            job.success_at = datetime.now()
        elif status == JobStatus.PENDING:
            job.started_at = datetime.now()
        elif status == JobStatus.FAILED:
            job.failed_at = datetime.now()

        await hset(job.id, job.model_dump())
    
    async def _consume_jobs(self, worker: JobWorker[Job]):
        while True:
            # print("\n\nListening for jobs...\n\n")
            job: Job | None = await self.queue.wait_for_next_job()
            if job is None:
                # delay for sometime before listening to the queue again
                await asyncio.sleep(15)
                print("Delay is done")
            else:
                print(f"Attempting job: {job.id}")
                await self._update_job_status(job, JobStatus.PENDING)
                try:
                    await worker.processor(*job.args, **job.kwargs)

                    await self._update_job_status(job, JobStatus.COMPLETED)
                    
                    print(f"Job {job.id} is finished")

                except Exception as e:
                    print(f"Failed to execute job with id: {job.id}. Message: {e}")

                    if job.current_attempts >= job.max_retry_attempts:
                        print(f"\n\nMaximum attempts reached. Updating {job.id} status to Failed")
                        await self._update_job_status(job, JobStatus.FAILED)
                    else:
                        job.current_attempts += 1

                        # exponential back off
                        delay = job.current_attempts**2
                        await asyncio.sleep(delay)
                        await self.queue.add_job(job)
        

    async def start(self, *, worker: JobWorker[Job], number_of_workers = 1):
        tasks = []
        for _ in range(number_of_workers):
            tasks.append(asyncio.create_task(self._consume_jobs(worker=worker)))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
