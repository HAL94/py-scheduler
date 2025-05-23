from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, Field, field_serializer


class Job(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the item (UUID string format)",
    )
    priority: Optional[int] = 0
    max_retry_attempts: Optional[int] = 0
    retry: Optional[bool] = False
    scheduled: Optional[bool] = False
    date: Optional[datetime] = datetime.now()
    
    @field_serializer('retry')
    def serialize_retry(self, retry: bool) -> str:
        return "1" if retry else "0"
    
    @field_serializer('scheduled')
    def serialize_scheduled(self, scheduled: bool) -> str:
        return "1" if scheduled else "0"
    
    @field_serializer('date')
    def serialize_date(self, date: datetime):
        return date.isoformat()
    


class ZRangeItem(BaseModel):
    key: str
    score: Optional[float] = None
