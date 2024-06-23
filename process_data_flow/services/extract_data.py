import asyncio

from tenacity import retry, stop_after_attempt, wait_fixed

from process_data_flow.commons.logger import Logger, LoggerFactory
from process_data_flow.commons.requests import MethodRequestEnum, make_async_request
from process_data_flow.commons.tenacity import warning_if_failed
from process_data_flow.services.rabbitmq import SendDataToRabbitMQService
from process_data_flow.settings import (
    EXTRACT_API_URL,
    PRODUCT_CONSUMER_EXCHANGE,
    PRODUCT_CONSUMER_KEY,
    RETRY_AFTER_SECONDS,
    RETRY_ATTEMPTS,
)


class SendExtractedDataService:
    def __init__(
        self,
        logger: Logger = LoggerFactory.new(),
    ):
        self.logger = logger

    @retry(
        reraise=True,
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_fixed(RETRY_AFTER_SECONDS),
        before=warning_if_failed,
    )
    async def _get_extracted_data(self):
        url = EXTRACT_API_URL + '/extract-data'
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

    def execute(self):
        self.logger.info('Sending extracted data to RabbitMQ...')

        send_data_to_rabbitmq = SendDataToRabbitMQService(self.logger)

        extracted_data = asyncio.run(self._get_extracted_data())

        send_data_to_rabbitmq.execute(
            items=extracted_data,
            exchange=PRODUCT_CONSUMER_EXCHANGE,
            routing_key=PRODUCT_CONSUMER_KEY,
        )

        self.logger.info(
            'Extracted data sent with successfully!',
            data=dict(total_items=len(extracted_data)),
        )


class FormatExtractedUrl:
    def __init__(self, logger: Logger = LoggerFactory.new()):
        self.logger = logger

    def _format_extracted_url(self, extracted_url: str) -> dict:
        base_url = 'https://www.magazineluiza.com.br'

        if not extracted_url.startswith(base_url):
            extracted_url = base_url + extracted_url

        return extracted_url

    def _load_extracted_url_from_rabbitmq(self, extracted_url_from_queue: bytes) -> str:
        return extracted_url_from_queue.decode()

    def execute(self, extracted_url_from_queue: bytes) -> str:
        self.logger.info('Executing Extracted url Service...')

        extracted_url = self._load_extracted_url_from_rabbitmq(extracted_url_from_queue)
        extracted_url = self._format_extracted_url(extracted_url)
        self.logger.info(
            'Extracted url formatted!', data=dict(extracted_url=extracted_url)
        )

        return extracted_url
