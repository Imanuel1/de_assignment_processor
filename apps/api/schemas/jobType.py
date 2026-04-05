from typing import Literal, Any
from pydantic import BaseModel

class EmailPayload(BaseModel):
    to: str
    subject: str
    body: str

class WebhookPayload(BaseModel):
    url: str
    method: Literal["GET", "POST"] = "POST"

class ReportPayload(BaseModel):
    report_type: str
    user_id: int

class BatchPayload(BaseModel):
    items: list[Any]
