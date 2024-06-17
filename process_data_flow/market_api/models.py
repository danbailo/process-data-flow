from pydantic import UUID4
from sqlmodel import Field, SQLModel


class ProductModel(SQLModel, table=True):
    __tablename__ = 'product'

    id: UUID4 = Field(primary_key=True)
    name: str
    price: float = Field(gt=0, lt=1000)
    observation: str | None = Field(min_length=80)
