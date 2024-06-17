import random

from process_data_flow.callback_api.schemas import ProductFactory, ProductSchema


def generate_fake_products(size: int = 1) -> list[ProductSchema]:
    return ProductFactory.batch(size)

def generate_random_data() -> list[ProductSchema]:
    should_return_value = random.choice([True, False])
    if not should_return_value:
        return []
    size = random.randint(1, 10)
    return generate_fake_products(size)
