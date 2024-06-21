import asyncio
import json

from tenacity import retry, stop_after_attempt, wait_fixed

from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.requests import MethodRequestEnum, make_async_request
from process_data_flow.commons.tenacity import warning_if_failed
from process_data_flow.schemas import ProductBody
from process_data_flow.services.rabbitmq import SendDataToRabbitMQService
from process_data_flow.settings import (
    EXTRACT_API_URL,
    PRODUCT_CONSUMER_EXCHANGE,
    PRODUCT_CONSUMER_KEY,
    RETRY_AFTER_SECONDS,
    RETRY_ATTEMPTS,
)


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


class SendProductService:
    def __init__(
        self,
        logger: Logger = LoggerFactory.new(),
    ):
        self.logger = logger

    @retry(
        reraise=True,
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_fixed(RETRY_AFTER_SECONDS),
        before=warning_if_failed,
    )
    async def _get_products(self):
        url = EXTRACT_API_URL + '/products'
        response = await make_async_request(MethodRequestEnum.GET, url)
        return response

    def execute(self):
        self.logger.info('Sending products to RabbitMQ...')

        send_data_to_rabbitmq = SendDataToRabbitMQService(self.logger)

        response = asyncio.run(self._get_products())
        products = response.json()['products']
        self.logger.debug(f'Was returned {len(products)} products')

        send_data_to_rabbitmq.execute(
            items=products,
            exchange=PRODUCT_CONSUMER_EXCHANGE,
            routing_key=PRODUCT_CONSUMER_KEY,
        )

        self.logger.info(
            'Products sent with successfully!', data=dict(total_items=len(products))
        )
