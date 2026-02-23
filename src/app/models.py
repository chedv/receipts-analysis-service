import uuid
from typing import Any

from sqlalchemy import Uuid, String, JSON
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class Receipt(Base):
    __tablename__ = "receipt"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50))
    text: Mapped[dict[str, Any]] = mapped_column(JSON)
