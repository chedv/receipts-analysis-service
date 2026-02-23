import asyncio

from aioboto3 import Session
from celery import shared_task

from src.app.schemas.auth_schemas import UserProfile
from src.app.repositories.receipt_repository import ReceiptRepository
from src.app.database import Database
from src.app.routers.dependencies import get_redis_client, get_receipt_service
from src.settings import settings


@shared_task
def start_receipt_ocr_task(file_name: str, receipt_id: str, user_id: str, user_email: str):
    with asyncio.Runner() as runner:
        runner.run(receipt_ocr_task(file_name=file_name, receipt_id=receipt_id, user_id=user_id, user_email=user_email))


async def receipt_ocr_task(file_name: str, receipt_id: str, user_id: str, user_email: str):
    async with Session().client(
        service_name="s3",
        region_name=settings.aws_region,
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    ) as s3_client:
        response = await s3_client.get_object(Bucket=settings.s3_bucket, Key=file_name)
        file_content = await response["Body"].read()

        redis_client = await get_redis_client()
        async with Database() as database:
            receipt_repository = ReceiptRepository()
            user_profile = UserProfile(user_id=user_id, user_email=user_email)
            receipt_service = await get_receipt_service(
                user_profile=user_profile,
                s3_client=s3_client,
                redis_client=redis_client,
                database=database,
                receipt_repository=receipt_repository,
            )
            await receipt_service.ocr(file_content, receipt_id, user_id)
