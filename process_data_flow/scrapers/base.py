import asyncio
from abc import ABC, abstractmethod

import httpx
from lxml import html

from process_data_flow.commons.logger import Logger, LoggerFactory


class BaseScraper(ABC):
    def __init__(self, logger: Logger = LoggerFactory.new()):
        self._client: httpx.AsyncClient = None
        self.logger = logger

    def __del__(self):
        if self._client is not None and not self._client.is_closed:
            self.logger.debug('Closing client...')
            asyncio.run(self._client.aclose())

    @property
    def client(self):
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers=self.headers, follow_redirects=True, verify=False
            )
        return self._client

    @property
    @abstractmethod
    def base_url(self):
        pass

    @property
    @abstractmethod
    def headers(self):
        pass

    def _get_elements_from_page(
        self, response: httpx.Response, xpath: str
    ) -> list[html.HtmlElement]:
        parsed_html: html.HtmlElement = html.fromstring(response.content)
        elements = parsed_html.xpath(xpath)
        self.logger.info(f'Extracted {len(elements)} elements')
        return elements
