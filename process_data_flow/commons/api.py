from math import ceil

from pydantic import BaseModel, model_serializer


class BuildListResponse(BaseModel):
    current_page: int
    limit: int
    total_items: int
    items: list

    @model_serializer
    def serialize_model(self):
        return {
            'total_items': self.total_items,
            'total_pages': ceil(self.total_items / self.limit),
            'items_per_page': self.limit,
            'current_page': self.current_page,
            'items': self.items,
        }
