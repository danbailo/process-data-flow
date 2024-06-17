from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import UUID4, BaseModel, Field


class ProductIn(BaseModel):
    name: str = Field(..., min_length=10)
    price: float = Field(..., gt=0, lt=1000)
    observation: str | None = Field(min_length=16)


class ProductOut(ProductIn):
    id: UUID4


class ProductFactory(ModelFactory[ProductOut]):
    __model__ = ProductOut
