import time
from abc import ABC, abstractmethod

from pika.channel import Channel
from pika.spec import Basic, BasicProperties
from pydantic import BaseModel

from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.rabbitmq.client import RabbitMQClient


class RabbitMQException(Exception):
    def __init__(self, message: str | None = None, requeue: bool | None = None) -> None:
        self.requeue = requeue
        super().__init__(message)


class RabbitMQConsumerOptions(BaseModel):
    queue: str = None
    auto_ack: bool = False
    exclusive: bool = False
    # consumer_tag=None
    arguments: dict = None
    requeue: bool = True


class RabbitMQConsumer(ABC):
    def __init__(
        self, options: RabbitMQConsumerOptions, logger: Logger = LoggerFactory.new()
    ):
        self.client = RabbitMQClient()
        self.logger = logger
        self.options = options
        self.client.channel.basic_qos(prefetch_count=1)

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
            monitoring=dict(queue=self.options.queue, message=body.decode())
        )
        self.logger.info('Consuming message')
        try:
            self._execute(ch, method, properties, body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            self.logger.info('Message consumed with sucessfully!')

        except Exception as err:
            requeue = getattr(err, 'requeue', None)
            if requeue is None:
                requeue = self.options.requeue

            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=requeue)
            self.logger.exception('An error has occured when consuming message!')

        time.sleep(1)

    def consume(self):
        self.logger.info('Starting consumer...', monitoring=self.options.model_dump())

        self.client.channel.basic_consume(
            queue=self.options.queue,
            auto_ack=self.options.auto_ack,
            exclusive=self.options.exclusive,
            arguments=self.options.arguments,
            on_message_callback=self._callback,
        )
        self.client.channel.start_consuming()
