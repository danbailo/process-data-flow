from math import ceil

from pydantic import BaseModel, model_serializer


class BuildListResponse(BaseModel):
    page: int
    limit: int
    total_items: int
    items: list[BaseModel]

    @model_serializer
    def serialize_model(self):
        return {
            'total_items': self.total_items,
            'total_pages': ceil(self.total_items / self.limit),
            'items_per_page': self.limit,
            'current_page': self.page,
            'items': self.items,
        }
