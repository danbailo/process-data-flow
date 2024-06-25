from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import UUID4
from sqlmodel import Session, func, select

from process_data_flow.apis.dependencies import get_session
from process_data_flow.apis.market.models import ExtractedUrlModel, ProductModel
from process_data_flow.commons.api import BuildListResponse
from process_data_flow.schemas import ProductIn, ProductOut

router = APIRouter(prefix='/product', tags=['product'])


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
    url: str | None = None,
    code: str | None = None,
    page: int = Query(1, gt=0),
    limit: int = Query(30, gt=0),
    session: Session = Depends(get_session),
):
    offset = (page - 1) * limit
    query = select(ProductModel, ExtractedUrlModel).join(
        ExtractedUrlModel, ProductModel.url_id == ExtractedUrlModel.id
    )

    if code:
        query = query.where(ProductModel.code == code)
    if url:
        query = query.where(ExtractedUrlModel.url == url)

    products = session.exec(query.offset(offset).limit(limit)).all()
    total_items = session.exec(select(func.count()).select_from(query)).one()

    items = [
        ProductOut(
            id=product.id,
            name=product.name,
            code=product.code,
            price=product.price,
            seller=product.seller,
            infos=product.infos,
            created_at=product.created_at,
            url=extracted_url.url,
        )
        for product, extracted_url in products
    ]
    to_return = BuildListResponse(
        current_page=page, limit=limit, total_items=total_items, items=items
    )
    return to_return


@router.post('', response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductIn, session: Session = Depends(get_session)):
    product_from_db = session.exec(
        select(ProductModel).where(ProductModel.code == product.code)
    ).first()
    if product_from_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Item {product.name} already exists!',
        )

    extracted_url_from_db = session.exec(
        select(ExtractedUrlModel).where(ExtractedUrlModel.url == product.url)
    ).first()
    if not extracted_url_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'The url {product.url} was not extracted!',
        )

    new_product = ProductModel(
        **product.model_dump(),
        url_id=extracted_url_from_db.id,
    )
    to_return = new_product.model_dump(mode='json')
    to_return.update({'url': extracted_url_from_db.url})
    session.add(new_product)
    session.commit()

    return to_return
