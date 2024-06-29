import time

import uvicorn
from typer import Option, Typer

from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.mp_scheduler import MPScheduler
from process_data_flow.commons.rabbitmq.consumer import RabbitMQConsumerOptions
from process_data_flow.consumers.market_query import MarketQueryConsumer
from process_data_flow.consumers.product import ProductConsumer
from process_data_flow.services.product import SendExtractDataToProductQueueService

logger: Logger = LoggerFactory.new()

app = Typer()

api = Typer()
scheduler = Typer()
consumer = Typer()


@api.command()
def magalu(
    port: int = Option(default=8081), reload: bool = Option(default=False, is_flag=True)
):
    uvicorn.run('process_data_flow.apis.magalu.app:app', port=port, reload=reload)


@api.command()
def market(
    port: int = Option(default=8082), reload: bool = Option(default=False, is_flag=True)
):
    uvicorn.run('process_data_flow.apis.market.app:app', port=port, reload=reload)


@scheduler.command()
def send_extract_data_to_rabbitmq(seconds: int = Option(default=3600)):
    mp_sched = MPScheduler()

    mp_sched.every(seconds).seconds.do(
        SendExtractDataToProductQueueService().execute,
    )

    while True:
        mp_sched.run_pending()
        time.sleep(1)


@consumer.command()
def product(
    auto_ack: bool = Option(default=False),
    exclusive: bool = Option(default=False),
    requeue: bool = Option(default=True),
):
    options = RabbitMQConsumerOptions(
        auto_ack=auto_ack,
        exclusive=exclusive,
        requeue=requeue,
    )
    product_consumer = ProductConsumer(options)
    product_consumer.consume()


@consumer.command()
def market_query(
    auto_ack: bool = Option(default=False),
    exclusive: bool = Option(default=False),
    requeue: bool = Option(default=True),
):
    options = RabbitMQConsumerOptions(
        auto_ack=auto_ack,
        exclusive=exclusive,
        requeue=requeue,
    )
    market_query_consumer = MarketQueryConsumer(options=options)
    market_query_consumer.consume()


app.add_typer(api, name='api')
app.add_typer(scheduler, name='scheduler')
app.add_typer(consumer, name='consumer')

app()
