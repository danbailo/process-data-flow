from contextlib import asynccontextmanager

from fastapi import FastAPI

from process_data_flow.apis.extractor.routers import extract_data, monitor, product
from process_data_flow.commons.logger import Logger, LoggerFactory

_logger: Logger = LoggerFactory.new()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _logger.debug(f'Started API - {app.title}')
    yield
    _logger.debug(f'Shutdown API - {app.title}')


app = FastAPI(title='Extractor API', lifespan=lifespan)


@app.get('/health')
async def health():
    return {'detail': 'ok'}


app.include_router(extract_data.route)
app.include_router(monitor.route)
app.include_router(product.route)
