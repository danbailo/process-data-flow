import asyncio
import json

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

from process_data_flow.callback_api.schemas import ProductSchema
from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.rabbitmq_client import RabbitMQClient
from process_data_flow.commons.tenacity import warning_if_failed
from process_data_flow.settings import (
    CALLBACK_API_URL,
    PRODUCT_CONSUMER_EXCHANGE,
    PRODUCT_CONSUMER_KEY,
    RETRY_AFTER_SECONDS,
    RETRY_ATTEMPTS,
)


class SendProductsToRabbitService:
    def __init__(
        self,
        logger: Logger = LoggerFactory.new(),
    ):
        self.rabbitmq = RabbitMQClient()
        self.logger = logger

    @retry(
        reraise=True,
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_fixed(RETRY_AFTER_SECONDS),
        before=warning_if_failed,
    )
    async def _get_products(self):
        url = CALLBACK_API_URL + '/products'

        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        response.raise_for_status()

        return response

    def _send_products_to_rabbitmq(self, products: list[dict]):
        for product in products:
            self.logger.info(
                'Product sent to RabbitMQ',
                data=dict(
                    product=product,
                    exchange=PRODUCT_CONSUMER_EXCHANGE,
                ),
            )
            self.rabbitmq.send_message(
                body=json.dumps(product),
                exchange=PRODUCT_CONSUMER_EXCHANGE,
                routing_key=PRODUCT_CONSUMER_KEY,
            )

    def execute(self):
        self.logger.info('Sending products to RabbitMQ...')

        response = asyncio.run(self._get_products())
        products = response.json()['products']
        self.logger.debug(f'Was returned {len(products)} products')
        self._send_products_to_rabbitmq(products)

        self.logger.info(
            'Products sent with successfully!', data=dict(len_products=len(products))
        )


class FormatProductService:
    def __init__(self, logger: Logger = LoggerFactory.new()):
        self.logger = logger

    def _format_product(self, product: dict) -> dict:
        product['name'] = f"{product['name'][:5]} {product['name'][5:]}"
        product['price'] = round(product['price'], 2)
        product['observation'] = (
            product['observation'][:16] * 2 if product['observation'] else None
        )
        return product

    def _load_product_from_rabbitmq(self, product_from_queue: bytes) -> ProductSchema:
        product_dict = json.loads(product_from_queue.decode())
        return ProductSchema(**product_dict)

    def execute(self, product_from_queue: bytes) -> ProductSchema:
        self.logger.info('Executing Format Product Service...')

        product = self._load_product_from_rabbitmq(product_from_queue)
        product_id = product.id

        to_return = self._format_product(product.model_dump(exclude={'id'}))
        self.logger.info('Product formatted!', data=dict(product_id=product_id))
        return ProductSchema(id=product_id, **to_return)
