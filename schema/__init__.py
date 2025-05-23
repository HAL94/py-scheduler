from datetime import datetime
import enum
import json
from typing import Annotated, Optional
import uuid
from pydantic import BaseModel, Field, WrapValidator, field_serializer


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    IDLE = "idle"

def validate_funcargs(value, handler):
    if not value:
        return None
    try:
        if isinstance(value, str):
            return json.loads(value)
        if isinstance(value, dict) or isinstance(value, list):
            return value
        
        return handler(value)
    except Exception:
        return None

JobArgs = Annotated[Optional[list | dict], WrapValidator(validate_funcargs)]

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
    args: JobArgs = []
    kwargs: JobArgs = {}

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

    @field_serializer("args")
    def serialize_args(self, args: list):
        if not args:
            return None
        return json.dumps(args)

    @field_serializer("kwargs", when_used="unless-none")
    def serialize_kwargs(self, kwargs: dict):
        if not kwargs:
            return None
        return json.dumps(kwargs)

    def model_dump(self, **kwargs):
        if "exclude_unset" not in kwargs:
            kwargs["exclude_unset"] = True

        return super().model_dump(**kwargs)


class ZRangeItem(BaseModel):
    key: str
    score: Optional[float] = None
