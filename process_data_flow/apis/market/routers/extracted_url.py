from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import UUID4
from sqlmodel import Session, func, select

from process_data_flow.apis.dependencies import get_session
from process_data_flow.apis.market.models import ExtractedUrlModel
from process_data_flow.commons.api import BuildListResponse
from process_data_flow.schemas import ExtractedUrlIn, ExtractedUrlOut

router = APIRouter(prefix='/extracted-url', tags=['extracted-url'])


@router.get('/{id}')
async def get_extracted_url(id: UUID4, session: Session = Depends(get_session)):
    extracted_url = session.exec(
        select(ExtractedUrlModel).where(ExtractedUrlModel.id == id)
    ).first()
    if extracted_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Extracted url with ID {id} does not exists!',
        )
    return extracted_url


@router.get('')
async def get_extracted_urls(
    url: str | None = None,
    page: int = Query(1, gt=0),
    limit: int = Query(30, gt=0),
    session: Session = Depends(get_session),
):
    offset = (page - 1) * limit
    query = select(ExtractedUrlModel)

    if url:
        query = query.where(ExtractedUrlModel.url == url)

    extracted_urls = session.exec(query.offset(offset).limit(limit)).all()
    total_items = session.exec(select(func.count()).select_from(query)).one()

    to_return = BuildListResponse(
        current_page=page, limit=limit, total_items=total_items, items=extracted_urls
    )
    return to_return


@router.post('', response_model=ExtractedUrlOut, status_code=status.HTTP_201_CREATED)
async def create_extracted_url(
    extracted_url: ExtractedUrlIn, session: Session = Depends(get_session)
):
    extracted_url_from_db = session.exec(
        select(ExtractedUrlModel).where(ExtractedUrlModel.url == extracted_url.url)
    ).first()
    if extracted_url_from_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Item {extracted_url_from_db.id} already exists!',
        )

    new_extracted_url = ExtractedUrlModel(**extracted_url.model_dump())
    session.add(new_extracted_url)
    session.commit()

    return new_extracted_url
