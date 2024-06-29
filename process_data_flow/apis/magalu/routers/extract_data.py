from fastapi import APIRouter, Query

from process_data_flow.clients.magalu import MagaluAPIClient
from process_data_flow.commons.api import BuildListResponse
from process_data_flow.scrapers.magalu import MagaluScraper

from process_data_flow.commons.requests import make_async_request, MethodRequestEnum
from process_data_flow.settings import MAGALU_API_URL
from process_data_flow.schemas import ExtractedUrlIn

router = APIRouter(prefix='/extract-data', tags=['extract-data'])


@router.post('')
async def extract_data_from_product(
    body: ExtractedUrlIn,
):
    magalu_scraper = MagaluScraper()

    extracted_data = await magalu_scraper.extract_data_from_product(body.url)

    return extracted_data
