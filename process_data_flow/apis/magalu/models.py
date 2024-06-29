from datetime import UTC, datetime
from uuid import uuid4

from pydantic import UUID4
from sqlmodel import Field, SQLModel


class MonitoredProductModel(SQLModel, table=True):
    __tablename__ = 'monitored_product'

    id: UUID4 = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)
    created_at: datetime = Field(default=datetime.now(UTC))
