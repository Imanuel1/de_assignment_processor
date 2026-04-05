
from datetime import datetime
from typing import Annotated, Annotated, Literal, Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field

from apps.api.common.enum import JobStatus
from apps.api.schemas.jobType import BatchPayload, BatchPayload, EmailPayload, ReportPayload, WebhookPayload


class JobRequest(BaseModel):
    job_type: Literal["email", "webhook", "report", "batch"]
    payload: Annotated[Union[EmailPayload, WebhookPayload, ReportPayload, BatchPayload], Field(discriminator="job_type")]
    priority: int = Field(default=1, ge=1, le=10)
    scheduled_time: Optional[datetime] = None
    idempotency_key: str

class JobResponse(JobRequest):
    id: UUID
    status: JobStatus
    created_at: int
    started_at: Optional[int] = None
    completed_at: Optional[int] = None
    attempts: int = 0
    progress: Optional[float] = None
    result: Optional[dict] = None
    error: Optional[str] = None



