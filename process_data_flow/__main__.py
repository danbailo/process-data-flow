import time

import uvicorn
from typer import Option, Typer

from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.mp_scheduler import MPScheduler
from process_data_flow.services.product import SendExtractDataToProductQueueService

logger: Logger = LoggerFactory.new()

app = Typer()

api = Typer()
scheduler = Typer()


@api.command()
def extractor(
    port: int = Option(default=8081), reload: bool = Option(default=False, is_flag=True)
):
    uvicorn.run('process_data_flow.apis.extractor.app:app', port=port, reload=reload)


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


app.add_typer(api, name='api')
app.add_typer(scheduler, name='scheduler')

app()
