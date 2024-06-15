import asyncio

from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.repositories.product import ProductRepository


class SendProductsToRabbitService:
    def __init__(
        self,
        product_repository: ProductRepository,
        logger: Logger = LoggerFactory.new(),
    ):
        self.product_repository = product_repository
        self.logger = logger

    def execute(self):
        self.logger.info('Sending products to RabbitMQ...')

        response = asyncio.run(self.product_repository.get_products())
        products = response.json()['products']
        self.logger.debug(f'Was returned {len(products)} products')
        self.product_repository.send_products_to_rabbitmq(products)

        self.logger.info('Products sent with successfully!')
