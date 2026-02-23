import uuid

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncConnection
from starlette import status

from src.app.repositories.receipt_repository import ReceiptRepository
from src.app.routers.dependencies import (
    get_receipt_service,
    get_receipt_repository,
    get_async_db_connection,
    authenticate,
)
from src.app.schemas.receipt_schemas import (
    ReceiptUploadResponseModel,
    ReceiptStatusResponseModel,
    ReceiptOcrResultResponseModel,
)
from src.app.services.receipt_service import ReceiptService

router = APIRouter()


@router.post("/upload", response_model=ReceiptUploadResponseModel)
@authenticate
async def receipt_upload(
    receipt_file: UploadFile = File(...),
    receipt_service: ReceiptService = Depends(get_receipt_service),
):
    file_content = await receipt_file.read()
    if not (file_name := receipt_file.filename):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File name is required")
    receipt_id = await receipt_service.upload(file_content=file_content, file_name=file_name)
    return {"receipt_id": receipt_id}


@router.get("/status/{receipt_id}", response_model=ReceiptStatusResponseModel)
@authenticate
async def get_receipt_status(
    receipt_id: uuid.UUID,
    receipt_service: ReceiptService = Depends(get_receipt_service),
):
    return await receipt_service.get_receipt_status(receipt_id=receipt_id)


@router.get("/result/{receipt_id}", response_model=ReceiptOcrResultResponseModel)
@authenticate
async def get_receipt_result(
    receipt_id: uuid.UUID,
    receipt_repository: ReceiptRepository = Depends(get_receipt_repository),
    connection: AsyncConnection = Depends(get_async_db_connection),
):
    raw_receipt_text = await receipt_repository.get_raw_receipt_text(str(receipt_id), connection)
    return {"receipt_text": raw_receipt_text}
