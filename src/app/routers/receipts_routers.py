import uuid

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from starlette import status

from src.app.routers.dependencies import get_receipt_service
from src.app.schemas.receipt_schemas import ReceiptUploadResponseModel, ReceiptStatusResponseModel
from src.app.services.receipt_service import ReceiptService

router = APIRouter()


@router.post("/upload", response_model=ReceiptUploadResponseModel)
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
async def get_receipt_status(
    receipt_id: uuid.UUID,
    receipt_service: ReceiptService = Depends(get_receipt_service),
):
    return await receipt_service.get_receipt_status(receipt_id=receipt_id)
