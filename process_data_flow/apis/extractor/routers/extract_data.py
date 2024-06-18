from fastapi import APIRouter

from process_data_flow.scrapers.magalu import MagaluScraper

route = APIRouter(prefix='/extract-data', tags=['extract-data'])

# TODO: paging with redis?
@route.get('/start')
async def extract_data_from_monitored_products():
    pass


@route.get('/start/{product}')
async def extract_data_from_product(product: str):
    magalu_scraper = MagaluScraper()
    items = await magalu_scraper.get_products_from_first_page(product)
    return {
        'total_items': len(items),
        'items': items,
    }
