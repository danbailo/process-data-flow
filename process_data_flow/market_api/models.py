from pydantic import UUID4
from sqlmodel import Field, SQLModel


class ProductModel(SQLModel, table=True):
    __tablename__ = 'product'

    id: UUID4 = Field(primary_key=True, index=True)
    name: str
    price: float
    observation: str | None
