from contextlib import asynccontextmanager

from fastapi import FastAPI

from process_data_flow.apis.database import init_db
from process_data_flow.apis.magalu.routers import extract_data, monitor, search
from process_data_flow.commons.logger import Logger, LoggerFactory

_logger: Logger = LoggerFactory.new()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _logger.debug(f'Started API - {app.title}')
    init_db()
    yield
    _logger.debug(f'Shutdown API - {app.title}')


app = FastAPI(title='Magalu API', lifespan=lifespan)


@app.get('/health')
async def health():
    return {'detail': 'ok'}


app.include_router(extract_data.router)
app.include_router(monitor.router)
app.include_router(search.router)
