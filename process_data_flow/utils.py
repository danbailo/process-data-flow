import random

from process_data_flow.schemas import ProductFactory, ProductOut


def generate_fake_products(size: int = 1) -> list[ProductOut]:
    return ProductFactory.batch(size)


def random_generate_fake_products() -> list[ProductOut]:
    should_return_value = random.choice([True, False])
    if not should_return_value:
        return []
    size = random.randint(1, 10)
    return generate_fake_products(size)
