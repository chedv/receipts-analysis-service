from typing import Any

import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncConnection

from src.app.models import Receipt


class ReceiptRepository:
    async def add_raw_receipt_text(self, receipt_id: str, receipt_text: Any, user_id: str, connection: AsyncConnection):
        await connection.execute(
            sa.insert(Receipt).values(
                {
                    "id": receipt_id,
                    "user_id": user_id,
                    "text": receipt_text,
                }
            )
        )

    async def get_raw_receipt_text(self, receipt_id: str, user_id: str, connection: AsyncConnection) -> Any:
        cursor = await connection.execute(
            sa.select(Receipt.text).where(and_(Receipt.id == receipt_id, Receipt.user_id == user_id))
        )
        row = cursor.fetchone()
        return row.text
