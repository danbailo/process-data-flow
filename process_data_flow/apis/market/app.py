from contextlib import asynccontextmanager

from fastapi import FastAPI

from process_data_flow.apis.database import init_db
from process_data_flow.apis.market.routers import product
from process_data_flow.commons.logger import Logger, LoggerFactory

_logger: Logger = LoggerFactory.new()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _logger.debug(f'Started API - {app.title}')
    init_db()
    yield
    _logger.debug(f'Shutdown API - {app.title}')


app = FastAPI(title='Market API', lifespan=lifespan)

app.include_router(product.router)


@app.get('/health')
async def health():
    return {'detail': 'ok'}
