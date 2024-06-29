from fastapi import APIRouter

from process_data_flow.schemas import ExtractedUrlIn
from process_data_flow.scrapers.magalu import MagaluScraper

router = APIRouter(prefix='/extract-data', tags=['extract-data'])


@router.post('')
async def extract_data_from_product(
    body: ExtractedUrlIn,
):
    magalu_scraper = MagaluScraper()

    extracted_data = await magalu_scraper.extract_data_from_product(body.url)

    return extracted_data
