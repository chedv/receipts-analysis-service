import uuid
from typing import Any

from pydantic import BaseModel

from src.app.schemas.celery_schemas import TaskStatus


class ReceiptUploadResponseModel(BaseModel):
    receipt_id: uuid.UUID


class ReceiptStatusResponseModel(BaseModel):
    status: TaskStatus
    detail: str | None = None


class ReceiptOcrResultResponseModel(BaseModel):
    receipt_text: Any
