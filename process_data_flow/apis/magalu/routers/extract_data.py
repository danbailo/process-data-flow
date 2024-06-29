from fastapi import APIRouter

from process_data_flow.crawlers.magalu import MagaluCrawler
from process_data_flow.schemas import ExtractedUrlIn

router = APIRouter(prefix='/extract-data', tags=['extract-data'])


@router.post('')
async def extract_data_from_product(
    body: ExtractedUrlIn,
):
    magalu_crawler = MagaluCrawler()
    extracted_data = await magalu_crawler.extract_data_from_product(body.url)
    return extracted_data
