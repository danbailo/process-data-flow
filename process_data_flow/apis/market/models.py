from datetime import UTC, datetime
from uuid import uuid4

from pydantic import UUID4
from sqlmodel import Field, SQLModel


class ProductModel(SQLModel, table=True):
    __tablename__ = 'product'

    id: UUID4 = Field(default=uuid4(), primary_key=True, index=True)
    name: str
    name_slug: str = Field(unique=True, index=True)
    price: float = Field(index=True)
    url: str = Field(unique=True)
    seller: str = Field(index=True)
    infos: str | None
    created_at: datetime = Field(default=datetime.now(UTC))
