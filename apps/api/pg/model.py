import uuid

from sqlalchemy import UUID, Column, DateTime, Float, Integer, String, JSONB

from apps.api.common.enum import JobStatus


class JobTable:
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    job_type = Column(String, nullable=False)
    payload = Column(JSONB, nullable=False)
    priority = Column(Integer, default=1)
    scheduled_time = Column(DateTime, nullable=True)
    idempotency_key = Column(String, nullable=False, unique=True)
    status= Column(String, default=JobStatus.PENDING.value)
    created_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    attempts = Column(Integer, default=1)
    progress = Column(Float, nullable=True)
    result = Column(JSONB, nullable=True)
    error = Column(String, nullable=True)
