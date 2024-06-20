import pika
from tenacity import retry, stop_after_attempt, wait_fixed

from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.settings import (
    RABBITMQ_HOST,
    RETRY_AFTER_SECONDS,
    RETRY_ATTEMPTS,
)


class NotRouteException(Exception):
    def __init__(self, message: str = 'Needed "exchange" or "routing_key"!') -> None:
        super().__init__(message)


class RabbitMQClient:
    def __init__(self, host: str = RABBITMQ_HOST, logger: Logger = LoggerFactory.new()):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host, connection_attempts=12, retry_delay=5)
        )
        self.channel = self.connection.channel()
        self.logger = logger

    @retry(
        reraise=True,
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_fixed(RETRY_AFTER_SECONDS),
    )
    def send_message(
        self, body: str, exchange: str = '', routing_key: str = '', **kwargs
    ):
        if not any([exchange, routing_key]):
            raise NotRouteException()

        self.channel.basic_publish(
            exchange=exchange, body=body, routing_key=routing_key, **kwargs
        )
