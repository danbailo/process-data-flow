from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import UUID4, BaseModel, Field, field_serializer


class ItemSchema(BaseModel):
    id: UUID4
    name: str
    price: float = Field(..., gt=0, lt=1000)
    observation: str | None

    @field_serializer('price')
    def format_value(value: float) -> float:
        return round(value, 2)


class ItemFactory(ModelFactory[ItemSchema]):
    __model__ = ItemSchema
