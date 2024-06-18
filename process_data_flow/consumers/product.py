
import asyncio

import httpx
from pika.channel import Channel
from pika.spec import Basic, BasicProperties
from tenacity import retry, stop_after_attempt, wait_fixed

from process_data_flow.commons.rabbitmq.consumer import (
    RabbitMQConsumer,
    RabbitMQConsumerOptions,
)
from process_data_flow.commons.tenacity import warning_if_failed
from process_data_flow.services.product import FormatProductService
from process_data_flow.settings import (
    MARKET_API_URL,
    MARKET_QUERY_EXCHANGE,
    MARKET_QUERY_KEY,
    PRODUCT_CONSUMER_QUEUE,
    RETRY_AFTER_SECONDS,
    RETRY_ATTEMPTS,
)


class ItemAlreadyExists(Exception):
    def __init__(self, message: str = 'Item already exists in database!') -> None:
        super().__init__(message)


class ProductConsumer(RabbitMQConsumer):
    def __init__(self) -> None:
        options = RabbitMQConsumerOptions(
            queue=PRODUCT_CONSUMER_QUEUE,
        )
        super().__init__(options=options)

    @retry(
        reraise=True,
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_fixed(RETRY_AFTER_SECONDS),
        before=warning_if_failed,
    )
    async def _get_product(self, id: str):
        url = MARKET_API_URL + f'/product/{id}'

        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        data = response.json()
        if isinstance(data, dict) and ('not exists' in data.get('detail', '')):
            return response

        response.raise_for_status()

        return response

    @retry(
        reraise=True,
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_fixed(RETRY_AFTER_SECONDS),
        before=warning_if_failed,
    )
    async def _create_product(self, data: dict):
        url = MARKET_API_URL + '/product'

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
        response.raise_for_status()

        return response

    def _execute(
        self,
        ch: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ):
        format_product_service = FormatProductService(self.logger)
        product = format_product_service.execute(body)

        response = asyncio.run(self._get_product(product.id))

        if response.status_code == 200:
            raise ItemAlreadyExists()

        asyncio.run(self._create_product(product.model_dump(mode='json')))

        self.client.send_message(
            exchange=MARKET_QUERY_EXCHANGE,
            routing_key=MARKET_QUERY_KEY,
            body=product.id.hex,
        )


if __name__ == '__main__':
    ProductConsumer().consume()
