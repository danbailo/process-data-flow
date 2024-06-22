from datetime import datetime

from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import UUID4, BaseModel, Field


class ProductBody(BaseModel):
    id: UUID4
    name: str = Field(..., min_length=10)
    price: float = Field(..., gt=0, lt=1000)
    observation: str | None = Field(min_length=16)


class ProductFactory(ModelFactory[ProductBody]):
    __model__ = ProductBody


class ProductIn(BaseModel):
    name: str
    price: float
    url: str
    seller: str
    infos: str | None = None


class ProductOut(ProductIn):
    id: UUID4
    name_slug: str
    created_at: datetime


class ExtractedUrlIn(BaseModel):
    url: str


class ExtractedUrlOut(ExtractedUrlIn):
    id: UUID4
    created_at: datetime


class MonitoredProductIn(BaseModel):
    name: str


class MonitoredProductOut(MonitoredProductIn):
    id: UUID4
    created_at: datetime
