import asyncio

from process_data_flow.commons.clients.magalu import MagaluAPIClient
from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.services.rabbitmq import SendDataToRabbitMQService
from process_data_flow.settings import (
    PRODUCT_CONSUMER_EXCHANGE,
    PRODUCT_CONSUMER_KEY,
)


class SendExtractDataToProductQueueService:
    def __init__(
        self,
        magalu_api_client: MagaluAPIClient = MagaluAPIClient(),
        logger: Logger = LoggerFactory.new(),
    ):
        self.magalu_api_client = magalu_api_client
        self.logger = logger

    def execute(self):
        send_data_to_rabbitmq = SendDataToRabbitMQService()

        data = asyncio.run(self.magalu_api_client.get_urls_from_monitored_products())
        send_data_to_rabbitmq.execute(
            items=data,
            exchange=PRODUCT_CONSUMER_EXCHANGE,
            routing_key=PRODUCT_CONSUMER_KEY,
        )
