from jobs.base_job_store import BaseJobStore
from schema import Job


class RedisJobStore(BaseJobStore[Job]):
    __model__ = Job

    async def save_job(self, name: str, data: Job) -> None:
        """
        Save the job to the redis hash by given name with data of Job

        Args:
            name: the key of the job
            data: the job's data
        """
        try:
            if not data:
                raise ValueError("Data must not be None")

            await self.client.hset(name=name, mapping=data.model_dump())
        except Exception as e:
            print(f"error occured at func: HSET: {e}")

    async def get_job(self, name: str) -> Job | None:
        """
        Get a job by name from redis Hash

        Args:
            name: the key of the job's data
        """

        try:
            item_dict = await self.client.hgetall(name=name)

            if not item_dict or len(item_dict) == 0:
                return None

            item_dict = {k.decode(): v.decode() for k, v in item_dict.items()}

            data = self._model(**item_dict)            

            if not data:
                return None

            return data

        except Exception as e:
            print(f"error occured at func: HGETALL: {e}")
