from abc import ABC, abstractmethod

from pika.channel import Channel
from pika.spec import Basic, BasicProperties
from pydantic import BaseModel

from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.rabbitmq_client import RabbitMQClient
from process_data_flow.services.product import FormatProductService
from process_data_flow.settings import PRODUCT_CONSUMER_QUEUE


class RabbitMQConsumerOptions(BaseModel):
    queue: str
    auto_ack: bool = False
    exclusive: bool = False
    # consumer_tag=None
    arguments: dict = None


class RabbitMQConsumer(ABC):
    def __init__(
        self, options: RabbitMQConsumerOptions, logger: Logger = LoggerFactory.new()
    ):
        self.client = RabbitMQClient()
        self.logger = logger
        self.client.channel.basic_qos(prefetch_count=1)

        self.options = options

    @abstractmethod
    def _handle_message(
        self,
        ch: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
        exc: Exception | None = None,
    ):
        pass

    @abstractmethod
    def _execute(
        self,
        ch: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ):
        pass

    def _callback(
        self,
        ch: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ):
        self.logger = self.logger.new(
            monitoring=dict(queue=self.options.queue, body=body.decode())
        )
        try:
            self._execute(ch, method, properties, body)
            self._handle_message(ch, method, properties, body)
            self.logger.debug('Error when consuming message!')
        except Exception as exc:
            self.logger.debug('Error when consuming message!')
            self._handle_message(ch, method, properties, body, exc)

    def consume(self):
        self.logger.info('Consuming queue', monitoring=dict(queue=self.options.queue))

        options = self.options.model_dump(exclude_none=True)
        self.client.channel.basic_consume(**options, on_message_callback=self._callback)
        self.client.channel.start_consuming()


class ProductConsumer(RabbitMQConsumer):
    def __init__(self) -> None:
        options = RabbitMQConsumerOptions(
            queue=PRODUCT_CONSUMER_QUEUE,
        )
        super().__init__(options=options)

    def _handle_message(
        self,
        ch: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
        exc: Exception | None = None,
    ):
        if exc is None:
            self.client.channel.basic_ack(delivery_tag=method.delivery_tag)
            self.logger.info('Message consumed with sucessfully!')
        else:
            self.client.channel.basic_nack(delivery_tag=method.delivery_tag)
            self.logger.exception('Error when consuming message!')

    def _execute(
        self,
        ch: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ):
        format_product_service = FormatProductService(self.logger)
        product = format_product_service.execute(body)


if __name__ == '__main__':
    ProductConsumer().consume()
