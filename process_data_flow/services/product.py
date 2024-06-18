import json

from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.schemas import ProductBody


class FormatProductService:
    def __init__(self, logger: Logger = LoggerFactory.new()):
        self.logger = logger

    def _format_product(self, product: dict) -> dict:
        product['name'] = f"{product['name'][:5]} {product['name'][5:]}"
        product['price'] = float(f"{product['price']:0.2f}")
        product['observation'] = (
            product['observation'][:16] * 2 if product['observation'] else None
        )
        return product

    def _load_product_from_rabbitmq(self, product_from_queue: bytes) -> ProductBody:
        product_dict = json.loads(product_from_queue.decode())
        return ProductBody(**product_dict)

    def execute(self, product_from_queue: bytes) -> ProductBody:
        self.logger.info('Executing Format Product Service...')

        product = self._load_product_from_rabbitmq(product_from_queue)
        product_id = product.id

        to_return = self._format_product(product.model_dump(exclude={'id'}))
        self.logger.info('Product formatted!', data=dict(product_id=product_id))
        return ProductBody(id=product_id, **to_return)
