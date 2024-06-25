from datetime import UTC, datetime
from uuid import uuid4

from pydantic import UUID4
from sqlmodel import Field, SQLModel


class ExtractedUrlModel(SQLModel, table=True):
    __tablename__ = 'extracted_url'

    id: UUID4 = Field(default_factory=uuid4, primary_key=True, index=True)
    url: str = Field(unique=True)
    created_at: datetime = Field(default=datetime.now(UTC))


class ProductModel(SQLModel, table=True):
    __tablename__ = 'product'

    id: UUID4 = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str
    code: str = Field(unique=True, index=True)
    price: float = Field(index=True)
    seller: str = Field(index=True)
    infos: str | None
    created_at: datetime = Field(default=datetime.now(UTC))

    url_id: UUID4 = Field(foreign_key='extracted_url.id')
