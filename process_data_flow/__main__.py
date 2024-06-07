import typer

from process_data_flow.commons.decorators import coro
from process_data_flow.commons.logger import Logger, LoggerFactory

logger: Logger = LoggerFactory.new()

app = typer.Typer()


@app.callback()
def callback():
    pass


@app.command()
@coro
def async_execute(option: str = typer.Option()):
    logger.info(f'option: {option}')


@app.command()
def execute(option: str = typer.Option()):
    logger.info(f'option: {option}')


if __name__ == '__main__':
    app()
