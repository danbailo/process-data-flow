from process_data_flow.clients.base import BaseAPIClient
from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.requests import MethodRequestEnum, make_async_request
from process_data_flow.settings import (
    MARKET_API_URL,
)


class MarketAPIClient(BaseAPIClient):
    def __init__(
        self,
        host: str = MARKET_API_URL,
        logger: Logger = LoggerFactory.new(),
    ):
        super().__init__(host, logger)

    async def get_product(self, code: str):
        url = self.host + '/product'
        response = await make_async_request(
            MethodRequestEnum.GET, url, params={'code': code}
        )
        return response

    async def create_product(self, data: dict):
        url = self.host + '/product'
        response = await make_async_request(MethodRequestEnum.POST, url, json=data)
        return response

    async def get_extracted_url(self, url: str):
        url_ = self.host + '/extracted-url'
        response = await make_async_request(
            MethodRequestEnum.GET, url_, params={'url': url}
        )
        return response

    async def create_extracted_url(self, url: str):
        url_ = self.host + '/extracted-url'
        response = await make_async_request(
            MethodRequestEnum.POST, url_, json={'url': url}
        )
        return response
