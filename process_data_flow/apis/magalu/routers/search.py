from fastapi import APIRouter, Query

from process_data_flow.commons.api import BuildListResponse
from process_data_flow.commons.clients.magalu import MagaluAPIClient
from process_data_flow.crawlers.magalu import MagaluCrawler

router = APIRouter(prefix='/search', tags=['search'])


@router.get('')
async def get_urls_from_monitored_products(
    page: int = Query(1, gt=0),
    limit: int = Query(30, gt=0),
):
    magalu_crawler = MagaluCrawler()

    magalu_api_client = MagaluAPIClient()
    monitored_products = await magalu_api_client.get_monitored_products()
    extracted_data = []
    for monitored_product in monitored_products:
        extracted_data.extend(
            await magalu_crawler.get_products_from_first_page(monitored_product['name'])
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
async def get_urls_from_product(
    product: str,
    page: int = Query(1, gt=0),
    limit: int = Query(30, gt=0),
):
    magalu_crawler = MagaluCrawler()

    extracted_data = await magalu_crawler.get_products_from_first_page(product)

    offset = (page - 1) * limit
    to_return = BuildListResponse(
        current_page=page,
        limit=limit,
        total_items=len(extracted_data),
        items=extracted_data[offset : limit * page],
    )
    return to_return
