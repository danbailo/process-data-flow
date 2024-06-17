from contextlib import asynccontextmanager
from math import ceil

import uvicorn
from fastapi import Depends, FastAPI, Query
from pydantic import UUID4, BaseModel, model_serializer
from sqlmodel import Session, func, select

from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.market_api.database import get_session, init_db
from process_data_flow.market_api.models import ProductModel


class BuildListResponse(BaseModel):
    page: int
    limit: int
    total_items: int
    items: list[BaseModel]

    @model_serializer
    def serialize_model(self):
        return {
            'total_items': self.total_items,
            'total_pages': ceil(self.total_items / self.limit),
            'items_per_page': self.limit,
            'current_page': self.page,
            'items': self.items,
        }


_logger: Logger = LoggerFactory.new()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _logger.debug('started api')
    init_db()
    yield
    _logger.info('shutdown api')


app = FastAPI(lifespan=lifespan)


@app.get('/product/{id}', response_model=ProductModel)
async def get_product(id: UUID4, session: Session = Depends(get_session)):
    product = session.exec(select(ProductModel).where(ProductModel.id == id)).one()
    return product


@app.get('/product')
async def get_products(
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0),
    session: Session = Depends(get_session),
):
    offset = (page - 1) * limit
    total_items = session.exec(select(func.count()).select_from(ProductModel)).one()
    products = session.exec(select(ProductModel).offset(offset).limit(limit)).all()
    to_return = BuildListResponse(
        page=page, limit=limit, total_items=total_items, items=products
    )
    return to_return


@app.get('/health')
async def health():
    return {'detail': 'ok'}


if __name__ == '__main__':
    uvicorn.run(app, port=8082)
