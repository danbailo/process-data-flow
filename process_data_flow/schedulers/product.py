import asyncio
import json
import time

import httpx
import schedule
from tenacity import retry, stop_after_attempt, wait_fixed

from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.rabbitmq.client import RabbitMQClient
from process_data_flow.commons.tenacity import warning_if_failed
from process_data_flow.settings import (
    EXTRACT_API_URL,
    PRODUCT_CONSUMER_EXCHANGE,
    PRODUCT_CONSUMER_KEY,
    RETRY_AFTER_SECONDS,
    RETRY_ATTEMPTS,
)


class SendProductsToRabbitScheduler:
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
        url = EXTRACT_API_URL + '/products'

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


if __name__ == '__main__':
    send_products_to_rabbit = SendProductsToRabbitScheduler()

    schedule.every(10).seconds.do(send_products_to_rabbit.execute)

    while True:
        schedule.run_pending()
        time.sleep(1)
