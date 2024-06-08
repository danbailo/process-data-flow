import random

from process_data_flow.callback_api.schemas import ItemFactory, ItemSchema


def generate_random_data() -> list[ItemSchema]:
    should_return_value = random.choice([True, False])
    if not should_return_value:
        return []
    len_items = random.randint(1, 10)
    return ItemFactory.batch(len_items)
