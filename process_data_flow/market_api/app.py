from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import UUID4
from sqlmodel import Session, func, select

from process_data_flow.commons.api import BuildListResponse
from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.market_api.database import get_session, init_db
from process_data_flow.market_api.models import ProductModel
from process_data_flow.schemas import ProductBody

_logger: Logger = LoggerFactory.new()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _logger.debug('started api')
    init_db()
    yield
    _logger.info('shutdown api')


app = FastAPI(lifespan=lifespan)


@app.get('/product/{id}')
async def get_product(id: UUID4, session: Session = Depends(get_session)):
    product = session.exec(select(ProductModel).where(ProductModel.id == id)).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Product with ID {id} does not exists!',
        )
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


@app.post('/product', response_model=ProductBody, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductBody, session: Session = Depends(get_session)):
    product_from_db = session.exec(
        select(ProductModel).where(ProductModel.id == product.id)
    ).first()
    if product_from_db:
        raise HTTPException(
            status=status.HTTP_409_CONFLICT,
            detail=f'Item with ID {product_from_db.id} already exists!',
        )
    new_product = ProductModel(**product.model_dump())
    session.add(new_product)
    session.commit()
    return new_product


@app.get('/health')
async def health():
    return {'detail': 'ok'}


if __name__ == '__main__':
    uvicorn.run(app, port=8082)
