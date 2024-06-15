import json

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

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


class ProductRepository:
    def __init__(self, logger: Logger = LoggerFactory.new()):
        self.rabbitmq = RabbitMQClient()
        self.logger = logger

    @retry(
        reraise=True,
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_fixed(RETRY_AFTER_SECONDS),
        before=warning_if_failed,
    )
    async def get_products(self):
        url = CALLBACK_API_URL + '/products'

        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        response.raise_for_status()

        return response

    def send_products_to_rabbitmq(self, products: list[dict]):
        for product in products:
            self.logger.info(
                'Product sent to RabbitMQ',
                product=product,
                exchange=PRODUCT_CONSUMER_EXCHANGE,
            )
            self.rabbitmq.send_message(
                body=json.dumps(product),
                exchange=PRODUCT_CONSUMER_EXCHANGE,
                routing_key=PRODUCT_CONSUMER_KEY,
            )
