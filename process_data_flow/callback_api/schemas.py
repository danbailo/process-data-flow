from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import UUID4, BaseModel, Field


class ProductSchema(BaseModel):
    id: UUID4
    name: str
    price: float = Field(..., gt=0, lt=1000)
    observation: str | None = Field(min_length=80)


class ProductFactory(ModelFactory[ProductSchema]):
    __model__ = ProductSchema
