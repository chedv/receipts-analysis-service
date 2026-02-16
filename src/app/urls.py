from fastapi import APIRouter

from src.app.routers import receipts_routers

router = APIRouter()

router.include_router(receipts_routers.router, prefix="/receipts")
