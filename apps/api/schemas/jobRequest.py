
from datetime import datetime
from typing import Literal, Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field

from apps.api.schemas.jobType import BatchPayload, BatchPayload, EmailPayload, ReportPayload, WebhookPayload


class JobRequest(BaseModel):
    job_type: Literal["email", "webhook", "report", "batch"]
    payload: Union[EmailPayload, WebhookPayload, ReportPayload, BatchPayload]
    priority: int = Field(default=1, ge=1, le=10)
    scheduled_time: Optional[datetime] = None
    idempotency_key: str

class JobResponse(JobRequest):
    id: UUID
    status: Literal["scheduled","pending", "processing", "completed", "failed", "canceled"]
    created_at: datetime
    attempts: int = 0
    progress: Optional[float] = None
    result: Optional[dict] = None
    error: Optional[str] = None



