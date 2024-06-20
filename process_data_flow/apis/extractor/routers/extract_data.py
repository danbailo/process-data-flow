from fastapi import APIRouter, Query

from process_data_flow.commons.api import BuildListResponse
from process_data_flow.commons.requests import MethodRequestEnum, make_async_request
from process_data_flow.scrapers.magalu import MagaluScraper
from process_data_flow.settings import EXTRACT_API_URL

router = APIRouter(prefix='/extract-data', tags=['extract-data'])


async def _get_monitored_products():
    url = EXTRACT_API_URL + '/monitor/product'

    monitored_products = []
    page = 1

    while True:
        response = await make_async_request(
            MethodRequestEnum.GET, url, params={'page': page, 'limit': 5}
        )
        data = response.json()
        monitored_products.extend(data['items'])

        if page == data['total_pages']:
            break
        page += 1

    return monitored_products


@router.get('/start')
async def extract_data_from_monitored_products(
    page: int = Query(1, gt=0),
    limit: int = Query(30, gt=0),
):
    magalu_scraper = MagaluScraper()

    monitored_products = await _get_monitored_products()

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


@router.get('/start/{product}')
async def extract_data_from_product(product: str):
    magalu_scraper = MagaluScraper()
    items = await magalu_scraper.get_products_from_first_page(product)
    return {
        'total_items': len(items),
        'items': items,
    }
