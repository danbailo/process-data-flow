import random

from process_data_flow.schemas import ProductBody, ProductFactory


def generate_fake_products(size: int = 1) -> list[ProductBody]:
    return ProductFactory.batch(size)


def random_generate_fake_products() -> list[ProductBody]:
    should_return_value = random.choice([True, False])
    if not should_return_value:
        return []
    size = random.randint(1, 10)
    return generate_fake_products(size)


def convert_seconds_to_milliseconds(value: int):
    return value * 1000
