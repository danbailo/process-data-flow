from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.rabbitmq.client import RabbitMQClient
from process_data_flow.settings import (
    MARKET_QUERY_DL_KEY,
    MARKET_QUERY_DLQ,
    MARKET_QUERY_DLX,
    MARKET_QUERY_EXCHANGE,
    MARKET_QUERY_KEY,
    MARKET_QUERY_QUEUE,
    PRODUCT_CONSUMER_EXCHANGE,
    PRODUCT_CONSUMER_KEY,
    PRODUCT_CONSUMER_QUEUE,
    REDIS_MESSAGE_TTL,
    REGISTER_PRODUCT_DL_KEY,
    REGISTER_PRODUCT_DLQ,
    REGISTER_PRODUCT_DLX,
    REGISTER_PRODUCT_EXCHANGE,
    REGISTER_PRODUCT_KEY,
    REGISTER_PRODUCT_QUEUE,
)
from process_data_flow.utils import convert_seconds_to_milliseconds


class RabbitMQConfig:
    def __init__(self, logger: Logger = LoggerFactory.new()):
        self.client = RabbitMQClient()
        self.logger = logger

        self.logger.debug('Configuring RabbitMQ...')
        self._configure_product_consumer()
        self._configure_market_query()
        self._configure_register_product()
        self.logger.info('RabbitMQ Configured!')

    def _configure_product_consumer(self):
        self.client.channel.exchange_declare(
            exchange=PRODUCT_CONSUMER_EXCHANGE, exchange_type='direct'
        )
        self.client.channel.queue_declare(queue=PRODUCT_CONSUMER_QUEUE, durable=True)
        self.client.channel.queue_bind(
            exchange=PRODUCT_CONSUMER_EXCHANGE,
            queue=PRODUCT_CONSUMER_QUEUE,
            routing_key=PRODUCT_CONSUMER_KEY,
        )

    def _configure_market_query(self):
        self.client.channel.exchange_declare(
            exchange=MARKET_QUERY_EXCHANGE, exchange_type='direct'
        )
        self.client.channel.queue_declare(
            queue=MARKET_QUERY_QUEUE,
            arguments={
                'x-dead-letter-exchange': MARKET_QUERY_DLX,
                'x-dead-letter-routing-key': MARKET_QUERY_DL_KEY,
            },
            durable=True,
        )
        self.client.channel.queue_bind(
            exchange=MARKET_QUERY_EXCHANGE,
            queue=MARKET_QUERY_QUEUE,
            routing_key=MARKET_QUERY_KEY,
        )

        self.client.channel.exchange_declare(
            exchange=MARKET_QUERY_DLX, exchange_type='direct'
        )
        self.client.channel.queue_declare(
            queue=MARKET_QUERY_DLQ,
            arguments={
                'x-message-ttl': convert_seconds_to_milliseconds(REDIS_MESSAGE_TTL),
                'x-dead-letter-exchange': MARKET_QUERY_EXCHANGE,
                'x-dead-letter-routing-key': MARKET_QUERY_KEY,
            },
            durable=True,
        )
        self.client.channel.queue_bind(
            exchange=MARKET_QUERY_DLX,
            queue=MARKET_QUERY_DLQ,
            routing_key=MARKET_QUERY_DL_KEY,
        )

    def _configure_register_product(self):
        self.client.channel.exchange_declare(
            exchange=REGISTER_PRODUCT_EXCHANGE, exchange_type='direct'
        )
        self.client.channel.queue_declare(
            queue=REGISTER_PRODUCT_QUEUE,
            arguments={
                'x-dead-letter-exchange': REGISTER_PRODUCT_DLX,
                'x-dead-letter-routing-key': REGISTER_PRODUCT_DL_KEY,
            },
            durable=True,
        )
        self.client.channel.queue_bind(
            exchange=REGISTER_PRODUCT_EXCHANGE,
            queue=REGISTER_PRODUCT_QUEUE,
            routing_key=REGISTER_PRODUCT_KEY,
        )

        self.client.channel.exchange_declare(
            exchange=REGISTER_PRODUCT_DLX, exchange_type='direct'
        )
        self.client.channel.queue_declare(
            queue=REGISTER_PRODUCT_DLQ,
            arguments={
                'x-message-ttl': convert_seconds_to_milliseconds(REDIS_MESSAGE_TTL),
                'x-dead-letter-exchange': REGISTER_PRODUCT_EXCHANGE,
                'x-dead-letter-routing-key': REGISTER_PRODUCT_KEY,
            },
            durable=True,
        )
        self.client.channel.queue_bind(
            exchange=REGISTER_PRODUCT_DLX,
            queue=REGISTER_PRODUCT_DLQ,
            routing_key=REGISTER_PRODUCT_DL_KEY,
        )
