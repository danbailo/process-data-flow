import asyncio

from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from process_data_flow.clients.market import MarketAPIClient
from process_data_flow.commons.rabbitmq.consumer import (
    RabbitMQConsumer,
    RabbitMQConsumerOptions,
)
from process_data_flow.consumers.exceptions import ItemAlreadyExists
from process_data_flow.services.extract_data import FormatExtractedUrlService
from process_data_flow.settings import (
    MARKET_QUERY_EXCHANGE,
    MARKET_QUERY_KEY,
    PRODUCT_CONSUMER_QUEUE,
)


class ProductConsumer(RabbitMQConsumer):
    queue: str = PRODUCT_CONSUMER_QUEUE

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
        format_extracted_url = FormatExtractedUrlService(self.logger)
        data = format_extracted_url.execute(body)
        response = asyncio.run(market_api_client.get_extracted_url(data))

        if response.status_code == 200 and response.json()['items']:
            raise ItemAlreadyExists(requeue=False)

        asyncio.run(market_api_client.create_extracted_url(data))

        self.client.send_message(
            exchange=MARKET_QUERY_EXCHANGE,
            routing_key=MARKET_QUERY_KEY,
            body=data,
        )
