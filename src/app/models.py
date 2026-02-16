import uuid
from typing import Any

from sqlalchemy import Uuid, JSON
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class Receipt(Base):
    __tablename__ = "receipt"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    text: Mapped[dict[str, Any]] = mapped_column(JSON)
