import asyncio

from process_data_flow.clients.extractor import ExtractorAPIClient
from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.services.rabbitmq import SendDataToRabbitMQService
from process_data_flow.settings import (
    PRODUCT_CONSUMER_EXCHANGE,
    PRODUCT_CONSUMER_KEY,
)


class SendExtractDataToProductQueueService:
    def __init__(
        self,
        extractor_api_client: ExtractorAPIClient = ExtractorAPIClient(),
        logger: Logger = LoggerFactory.new(),
    ):
        self.extractor_api_client = extractor_api_client
        self.logger = logger

    def execute(self):
        send_data_to_rabbitmq = SendDataToRabbitMQService()

        data = asyncio.run(self.extractor_api_client.get_extracted_data())
        send_data_to_rabbitmq.execute(
            items=data,
            exchange=PRODUCT_CONSUMER_EXCHANGE,
            routing_key=PRODUCT_CONSUMER_KEY,
        )
