from process_data_flow.clients.base import BaseAPIClient
from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.requests import MethodRequestEnum, make_async_request
from process_data_flow.settings import (
    EXTRACT_API_URL,
)


class ExtractorAPIClient(BaseAPIClient):
    def __init__(
        self,
        host: str = EXTRACT_API_URL,
        logger: Logger = LoggerFactory.new(),
    ):
        super().__init__(host, logger)

    async def get_extracted_data(self):
        url = self.host + '/extract-data'
        extracted_data = await self.paging_requests(url)
        self.logger.info(f'Was extracted {len(extracted_data)} items')
        return extracted_data

    async def get_product(self):
        url = self.host + '/product'
        response = await make_async_request(MethodRequestEnum.GET, url)
        return response

    async def get_monitored_products(self):
        url = EXTRACT_API_URL + '/monitor/product'
        monitored_products = await self.paging_requests(url)
        return monitored_products
