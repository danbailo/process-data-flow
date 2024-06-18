
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import UUID4
from sqlmodel import Session, func, select

from process_data_flow.apis.market.database import get_session
from process_data_flow.apis.market.models import ProductModel
from process_data_flow.commons.api import BuildListResponse
from process_data_flow.schemas import ProductBody

router = APIRouter()


@router.get('/{id}')
async def get_product(id: UUID4, session: Session = Depends(get_session)):
    product = session.exec(select(ProductModel).where(ProductModel.id == id)).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Product with ID {id} does not exists!',
        )
    return product


@router.get('')
async def get_products(
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0),
    session: Session = Depends(get_session),
):
    offset = (page - 1) * limit
    total_items = session.exec(select(func.count()).select_from(ProductModel)).one()
    products = session.exec(select(ProductModel).offset(offset).limit(limit)).all()
    to_return = BuildListResponse(
        current_page=page, limit=limit, total_items=total_items, items=products
    )
    return to_return


@router.post('', response_model=ProductBody, status_code=status.HTTP_201_CREATED)
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
