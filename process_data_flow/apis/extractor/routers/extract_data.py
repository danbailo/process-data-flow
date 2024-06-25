from fastapi import APIRouter, Query

from process_data_flow.clients.extractor import ExtractorAPIClient
from process_data_flow.commons.api import BuildListResponse
from process_data_flow.scrapers.magalu import MagaluScraper

router = APIRouter(prefix='/extract-data', tags=['extract-data'])


@router.get('')
async def extract_data_from_monitored_products(
    page: int = Query(1, gt=0),
    limit: int = Query(30, gt=0),
):
    magalu_scraper = MagaluScraper()

    extractor_api_client = ExtractorAPIClient()
    monitored_products = await extractor_api_client.get_monitored_products()
    extracted_data = []
    for monitored_product in monitored_products:
        extracted_data.extend(
            await magalu_scraper.get_products_from_first_page(monitored_product['name'])
        )

    offset = (page - 1) * limit
    to_return = BuildListResponse(
        current_page=page,
        limit=limit,
        total_items=len(extracted_data),
        items=extracted_data[offset : limit * page],
    )

    return to_return


@router.get('/{product}')
async def extract_data_from_product(
    product: str,
    page: int = Query(1, gt=0),
    limit: int = Query(30, gt=0),
):
    magalu_scraper = MagaluScraper()

    extracted_data = await magalu_scraper.get_products_from_first_page(product)

    offset = (page - 1) * limit
    to_return = BuildListResponse(
        current_page=page,
        limit=limit,
        total_items=len(extracted_data),
        items=extracted_data[offset : limit * page],
    )
    return to_return
