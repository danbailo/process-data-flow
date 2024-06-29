import asyncio

from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from process_data_flow.clients.market import MarketAPIClient
from process_data_flow.commons.rabbitmq.consumer import (
    RabbitMQConsumer,
    RabbitMQConsumerOptions,
)
from process_data_flow.crawlers.register_product import RegisterProductCrawler
from process_data_flow.settings import REGISTER_PRODUCT_QUEUE


class RegisterProductConsumer(RabbitMQConsumer):
    queue: str = REGISTER_PRODUCT_QUEUE

    def __init__(self, options: RabbitMQConsumerOptions = RabbitMQConsumerOptions()):
        options.queue = self.queue
        super().__init__(options=options)

    def _execute(
        self,
        ch: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ):
        market_api_client = MarketAPIClient()
        register_product_crawler = RegisterProductCrawler()
        message = body.decode()

        response = asyncio.run(market_api_client.get_product_by_id(message))
        data = response.json()

        asyncio.run(register_product_crawler.submit_form(data))
