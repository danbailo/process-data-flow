import json

from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.rabbitmq.client import RabbitMQClient


class SendDataToRabbitMQService:
    def __init__(
        self,
        logger: Logger = LoggerFactory.new(),
    ):
        self.rabbitmq_client = RabbitMQClient()
        self.logger = logger

    def execute(self, *, items: list, exchange: str, routing_key: str):
        for item in items:
            self.rabbitmq_client.send_message(
                body=json.dumps(item),
                exchange=exchange,
                routing_key=routing_key,
            )
        self.logger.info('All items was sent to RabbitMQ with successfully!')
