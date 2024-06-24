from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.requests import MethodRequestEnum, make_async_request
from process_data_flow.settings import (
    MARKET_API_URL,
)


class MarketAPIClient:
    def __init__(
        self,
        host: str = MARKET_API_URL,
        logger: Logger = LoggerFactory.new(),
    ):
        self.host = host
        self.logger = logger

    async def get_product(self, code: str):
        url = MARKET_API_URL + '/product'
        response = await make_async_request(
            MethodRequestEnum.GET, url, params={'code': code}
        )
        return response

    async def create_product(self, data: dict):
        url = MARKET_API_URL + '/product'
        response = await make_async_request(MethodRequestEnum.POST, url, json=data)
        return response
