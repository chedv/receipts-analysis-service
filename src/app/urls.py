from fastapi import APIRouter

from src.app.routers import receipt_routers

router = APIRouter()

router.include_router(receipt_routers.router, prefix="/receipts")
