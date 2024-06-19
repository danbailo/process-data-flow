from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from process_data_flow.commons.rabbitmq.consumer import (
    RabbitMQConsumer,
    RabbitMQConsumerOptions,
)
from process_data_flow.settings import (
    MARKET_QUERY_QUEUE,
)


class MarketQueryConsumer(RabbitMQConsumer):
    def __init__(self) -> None:
        options = RabbitMQConsumerOptions(queue=MARKET_QUERY_QUEUE, requeue=False)
        super().__init__(options=options)

    def _execute(
        self,
        ch: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ):
        # breakpoint()
        raise Exception('foo')

        # self.client.send_message(
        #     exchange=MARKET_QUERY_EXCHANGE,
        #     routing_key=MARKET_QUERY_KEY,
        #     body=product.id.hex,
        # )


if __name__ == '__main__':
    MarketQueryConsumer().consume()
