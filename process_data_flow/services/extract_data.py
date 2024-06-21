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
