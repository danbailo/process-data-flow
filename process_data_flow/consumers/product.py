import asyncio

from pika.channel import Channel
from pika.spec import Basic, BasicProperties
from tenacity import retry, stop_after_attempt, wait_fixed

from process_data_flow.commons.rabbitmq.consumer import (
    RabbitMQConsumer,
    RabbitMQConsumerOptions,
)
from process_data_flow.commons.requests import MethodRequestEnum, make_async_request
from process_data_flow.commons.tenacity import warning_if_failed
from process_data_flow.consumers.exceptions import ItemAlreadyExists
from process_data_flow.services.extract_data import FormatExtractedUrlService
from process_data_flow.settings import (
    MARKET_API_URL,
    MARKET_QUERY_EXCHANGE,
    MARKET_QUERY_KEY,
    PRODUCT_CONSUMER_QUEUE,
    RETRY_AFTER_SECONDS,
    RETRY_ATTEMPTS,
)


class ProductConsumer(RabbitMQConsumer):
    def __init__(self) -> None:
        options = RabbitMQConsumerOptions(
            queue=PRODUCT_CONSUMER_QUEUE,
        )
        super().__init__(options=options)

    @retry(
        reraise=True,
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_fixed(RETRY_AFTER_SECONDS),
        before=warning_if_failed,
    )
    async def _get_extracted_url(self, url: str):
        url_ = MARKET_API_URL + '/extracted-url'
        response = await make_async_request(
            MethodRequestEnum.GET, url_, params={'url': url}
        )
        return response

    @retry(
        reraise=True,
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_fixed(RETRY_AFTER_SECONDS),
        before=warning_if_failed,
    )
    async def _create_extracted_url(self, url: str):
        url_ = MARKET_API_URL + '/extracted-url'
        response = await make_async_request(
            MethodRequestEnum.POST, url_, json={'url': url}
        )
        return response

    def _execute(
        self,
        ch: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ):
        format_extracted_url = FormatExtractedUrlService(self.logger)
        data = format_extracted_url.execute(body)
        response = asyncio.run(self._get_extracted_url(data))

        if response.status_code == 200 and response.json()['items']:
            raise ItemAlreadyExists(requeue=False)

        asyncio.run(self._create_extracted_url(data))

        self.client.send_message(
            exchange=MARKET_QUERY_EXCHANGE,
            routing_key=MARKET_QUERY_KEY,
            body=data,
        )


if __name__ == '__main__':
    ProductConsumer().consume()
