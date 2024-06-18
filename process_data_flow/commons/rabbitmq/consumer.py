from abc import ABC, abstractmethod

from pika.channel import Channel
from pika.spec import Basic, BasicProperties
from pydantic import BaseModel

from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.rabbitmq.client import RabbitMQClient


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
            ch.basic_ack(delivery_tag=method.delivery_tag)
            self.logger.info('Message consumed with sucessfully!')

        except Exception:
            ch.basic_nack(delivery_tag=method.delivery_tag)
            self.logger.exception('An error has occured when consuming message!')

    def consume(self):
        self.logger.info('Consuming queue', monitoring=dict(queue=self.options.queue))

        options = self.options.model_dump(exclude_none=True)
        self.client.channel.basic_consume(**options, on_message_callback=self._callback)
        self.client.channel.start_consuming()
