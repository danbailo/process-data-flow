import asyncio

from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from process_data_flow.commons.clients.magalu import MagaluAPIClient
from process_data_flow.commons.clients.market import MarketAPIClient
from process_data_flow.commons.rabbitmq.consumer import (
    RabbitMQConsumer,
    RabbitMQConsumerOptions,
)
from process_data_flow.consumers.exceptions import ItemAlreadyExists
from process_data_flow.services.extract_data import (
    FormatExtractedDataFromUrlService,
)
from process_data_flow.settings import (
    MARKET_QUERY_QUEUE,
    REGISTER_PRODUCT_EXCHANGE,
    REGISTER_PRODUCT_KEY,
)


class MarketQueryConsumer(RabbitMQConsumer):
    queue: str = MARKET_QUERY_QUEUE

    def __init__(
        self,
        market_api_client: MarketAPIClient = MarketAPIClient(),
        magalu_api_client: MagaluAPIClient = MagaluAPIClient(),
        options: RabbitMQConsumerOptions = RabbitMQConsumerOptions(),
    ):
        options.queue = self.queue
        options.requeue = False
        super().__init__(options=options)

        self.market_api_client = market_api_client
        self.magalu_api_client = magalu_api_client

    def _execute(
        self,
        ch: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ):
        message = body.decode()
        format_extracted_data = FormatExtractedDataFromUrlService()

        data = asyncio.run(self.magalu_api_client.extract_data_from_product(message))
        formatted_data = format_extracted_data.execute(data)

        response = asyncio.run(
            self.market_api_client.get_product(formatted_data['code'])
        )

        if response.status_code == 200 and response.json()['items']:
            raise ItemAlreadyExists(requeue=False)

        formatted_data['url'] = message
        response = asyncio.run(self.market_api_client.create_product(formatted_data))

        self.client.send_message(
            exchange=REGISTER_PRODUCT_EXCHANGE,
            routing_key=REGISTER_PRODUCT_KEY,
            body=response.json()['id'],
        )
