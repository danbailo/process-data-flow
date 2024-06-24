from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.requests import MethodRequestEnum, make_async_request
from process_data_flow.settings import (
    EXTRACT_API_URL,
)


class ExtractorAPIClient:
    def __init__(
        self,
        host: str = EXTRACT_API_URL,
        logger: Logger = LoggerFactory.new(),
    ):
        self.host = host
        self.logger = logger

    async def get_extracted_data(self):
        url = self.host + '/extract-data'
        extracted_data = []
        page = 1

        while True:
            response = await make_async_request(
                MethodRequestEnum.GET, url, params={'page': page, 'limit': 50}
            )
            data = response.json()
            extracted_data.extend(data['items'])

            if page == data['total_pages']:
                break
            page += 1

        self.logger.info(f'Was extracted {len(extracted_data)} items')
        return extracted_data

    async def _get_product(self):
        url = self.host + '/product'
        response = await make_async_request(MethodRequestEnum.GET, url)
        return response
