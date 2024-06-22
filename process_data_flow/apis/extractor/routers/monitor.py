from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, func, select

from process_data_flow.apis.dependencies import get_session
from process_data_flow.apis.extractor.models import MonitoredProductModel
from process_data_flow.commons.api import BuildListResponse
from process_data_flow.schemas import MonitoredProductIn, MonitoredProductOut

router = APIRouter(prefix='/monitor', tags=['monitor'])


@router.get('/product')
async def show_monitored_products(
    page: int = Query(1, gt=0),
    limit: int = Query(30, gt=0),
    session: Session = Depends(get_session),
):
    offset = (page - 1) * limit
    query = select(MonitoredProductModel)

    monitored_products = session.exec(query.offset(offset).limit(limit)).all()
    total_items = session.exec(select(func.count()).select_from(query)).one()

    to_return = BuildListResponse(
        current_page=page,
        limit=limit,
        total_items=total_items,
        items=monitored_products,
    )
    return to_return


@router.post(
    '/product', response_model=MonitoredProductOut, status_code=status.HTTP_201_CREATED
)
async def monitor_new_product(
    monitored_product: MonitoredProductIn, session: Session = Depends(get_session)
):
    monitored_product_from_db = session.exec(
        select(MonitoredProductModel).where(
            MonitoredProductModel.name == monitored_product.name
        )
    ).first()
    if monitored_product_from_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Monitored product with name {monitored_product_from_db.name} already exists!',
        )
    new_monitored_product = MonitoredProductModel(**monitored_product.model_dump())
    session.add(new_monitored_product)
    session.commit()
    return new_monitored_product


@router.delete('/product', status_code=status.HTTP_204_NO_CONTENT)
async def remove_product(
    monitored_product: MonitoredProductIn,
    session: Session = Depends(get_session),
):
    monitored_product_from_db = session.exec(
        select(MonitoredProductModel).where(
            MonitoredProductModel.name == monitored_product.name
        )
    ).first()
    if not monitored_product_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Monitored product with name {monitored_product.name} not exists!',
        )
    session.delete(monitored_product_from_db)
    session.commit()
