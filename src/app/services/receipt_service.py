import io
import json
import uuid

import redis.asyncio as redis
import sqlalchemy as sa
from paddleocr import PaddleOCR
from types_aiobotocore_s3 import S3Client

from src.app.celery import celery_app
from src.app.database import Database
from src.app.models import Receipt
from src.app.schemas.celery_schemas import TaskStatus
from src.settings import settings


class ReceiptService:
    def __init__(self, s3_client: S3Client, redis_client: redis.Redis, database: Database):
        self.s3_client = s3_client
        self.redis_client = redis_client
        self.database = database

    async def upload(self, file_content: bytes, file_name: str) -> uuid.UUID:
        await self.s3_client.put_object(Body=io.BytesIO(file_content), Bucket=settings.s3_bucket, Key=file_name)
        receipt_id = uuid.uuid4()
        task_kwargs = {"file_name": file_name, "receipt_id": str(receipt_id)}
        celery_app.send_task("src.app.tasks.receipt_ocr_task.start_receipt_ocr_task", kwargs=task_kwargs)
        await self.redis_client.set(f"receipt-{receipt_id}", json.dumps({"status": TaskStatus.CREATED}))
        return receipt_id

    async def get_receipt_status(self, receipt_id: uuid.UUID) -> dict:
        raw_value = await self.redis_client.get(f"receipt-{receipt_id}")
        return json.loads(raw_value)

    async def ocr(self, file_content: bytes, receipt_id: str):
        try:
            await self.redis_client.set(f"receipt-{receipt_id}", json.dumps({"status": TaskStatus.IN_PROGRESS}))
            result = PaddleOCR().ocr(file_content)
            async with self.database.transactional() as connection:
                await connection.execute(sa.insert(Receipt).values({"id": receipt_id, "text": result}))
            await self.redis_client.set(f"receipt-{receipt_id}", json.dumps({"status": TaskStatus.SUCCESS}))
        except Exception as e:
            cache_value = {"status": TaskStatus.FAILED, "detail": str(e)}
            await self.redis_client.set(f"receipt-{receipt_id}", json.dumps(cache_value))
