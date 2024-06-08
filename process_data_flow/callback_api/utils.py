import random

from process_data_flow.callback_api.schemas import ProductFactory, ProductSchema


def generate_random_data() -> list[ProductSchema]:
    should_return_value = random.choice([True, False])
    if not should_return_value:
        return []
    len_items = random.randint(1, 10)
    return ProductFactory.batch(len_items)
