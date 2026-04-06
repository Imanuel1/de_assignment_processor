
from datetime import datetime
from typing import Annotated, Annotated, Literal, Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field, model_validator

from apps.api.common.enum import JobStatus
from apps.api.schemas.jobType import BatchPayload, BatchPayload, EmailPayload, ReportPayload, WebhookPayload


class JobRequest(BaseModel):
    job_type: Literal["email", "webhook", "report", "batch"]
    payload: Union[EmailPayload, WebhookPayload, ReportPayload, BatchPayload]
    priority: int = Field(default=1, ge=1, le=10)
    scheduled_time: Optional[datetime] = None
    idempotency_key: str

    @model_validator(mode="after")
    def validate_payload_type(self):

        mapping = {
            "email": EmailPayload,
            "webhook": WebhookPayload,
            "report": ReportPayload,
            "batch": BatchPayload
        }
        
        expected_type = mapping.get(self.job_type)
        if not isinstance(self.payload, expected_type):
            raise ValueError(f"Payload must be of type {expected_type.__name__} for job_type '{self.job_type}'")
        return self

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



