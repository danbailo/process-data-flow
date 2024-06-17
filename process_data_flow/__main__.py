import uvicorn
from typer import Option, Typer

from process_data_flow.commons.logger import Logger, LoggerFactory

logger: Logger = LoggerFactory.new()

app = Typer()


@app.command()
def callback_api(
    port: int = Option(default=8081), reload: bool = Option(default=False, is_flag=True)
):
    uvicorn.run('process_data_flow.callback_api.app:app', port=port, reload=reload)


@app.command()
def market_api(
    port: int = Option(default=8082), reload: bool = Option(default=False, is_flag=True)
):
    uvicorn.run('process_data_flow.market_api.app:app', port=port, reload=reload)


if __name__ == '__main__':
    app()
