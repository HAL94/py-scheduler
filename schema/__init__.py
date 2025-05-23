from datetime import datetime
import enum
from typing import Optional
import uuid
from pydantic import BaseModel, Field, field_serializer


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    IDLE = "idle"
    
    

class Job(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the item (UUID string format)",
    )
    priority: Optional[int] = 0
    created_at: Optional[datetime] = datetime.now()
    scheduled_at: Optional[datetime] = datetime.now()
    started_at: Optional[datetime] = None
    success_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    task_name: str
    max_retry_attempts: Optional[int] = 0
    current_attempts: int = 0
    status: JobStatus = JobStatus.IDLE
    # args: Optional[tuple[Any]] = ()
    # kwargs: Optional[dict[str, Any]] = {}

    @field_serializer("created_at")
    def serialize_created_at(self, created_at: datetime):
        return created_at.isoformat()

    @field_serializer("scheduled_at")
    def serialize_scheduled_at(self, scheduled_at: datetime):
        return scheduled_at.isoformat()
    
    @field_serializer("started_at")
    def serialize_started_at(self, started_at: datetime):
        if not started_at:
            return None
        return started_at.isoformat()

    @field_serializer("failed_at")    
    def serialize_failed_at(self, failed_at: datetime):
        if not failed_at:
            return None
        return failed_at.isoformat()
    
    @field_serializer("success_at")
    def serialize_success_at(self, success_at: datetime):
        if not success_at:
            return None
        return success_at.isoformat()
    
    def model_dump(self, **kwargs):
        if "exclude_unset" not in kwargs:
            kwargs["exclude_unset"] = True
            
        return super().model_dump(**kwargs)

    # @field_serializer('args')
    # def serialize_args(self, args: tuple):
    #     return ", ".join(list(map(lambda item: str(item), list(args))))

    # @field_serializer('kwargs')
    # def serialize_kwargs(self, kwargs: dict):
    #     return str(kwargs)


class ZRangeItem(BaseModel):
    key: str
    score: Optional[float] = None



