from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.requests import MethodRequestEnum, make_async_request


class BaseAPIClient:
    def __init__(
        self,
        host: str,
        logger: Logger = LoggerFactory.new(),
    ):
        self.host = host
        self.logger = logger

    async def paging_requests(self, url: str, **kwargs) -> list:
        items = []
        page = 1

        while True:
            response = await make_async_request(
                MethodRequestEnum.GET,
                url,
                params={'page': page, 'limit': kwargs.get('limit', 30)},
                **kwargs,
            )
            data = response.json()
            items.extend(data['items'])

            if (data['total_pages'] == 0) or (page == data['total_pages']):
                break
            page += 1

        return items
