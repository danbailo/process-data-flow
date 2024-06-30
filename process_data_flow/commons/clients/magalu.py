from process_data_flow.commons.clients.base import BaseAPIClient
from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.requests import MethodRequestEnum, make_async_request
from process_data_flow.settings import (
    MAGALU_API_URL,
)


class MagaluAPIClient(BaseAPIClient):
    def __init__(
        self,
        host: str = MAGALU_API_URL,
        logger: Logger = LoggerFactory.new(),
    ):
        super().__init__(host, logger)

    async def get_urls_from_monitored_products(self):
        url = self.host + '/search'
        collected_data = await self.paging_requests(url)
        self.logger.info(f'Was collected {len(collected_data)} items')
        return collected_data

    async def get_product(self):
        url = self.host + '/product'
        response = await make_async_request(MethodRequestEnum.GET, url)
        return response

    async def get_monitored_products(self):
        url = MAGALU_API_URL + '/monitor/product'
        monitored_products = await self.paging_requests(url)
        return monitored_products

    async def extract_data_from_product(self, url: str):
        url_ = MAGALU_API_URL + '/extract-data'
        extracted_data = await make_async_request(
            MethodRequestEnum.POST, url_, json={'url': url}
        )
        return extracted_data.json()
