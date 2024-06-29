from abc import ABC, abstractmethod

import httpx
from lxml import html

from process_data_flow.commons.logger import Logger, LoggerFactory


class BaseCrawler(ABC):
    def __init__(self, logger: Logger = LoggerFactory.new()):
        self._client: httpx.AsyncClient = None
        self.logger = logger

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

    def build_html(self, response: httpx.Response) -> html.HtmlElement:
        parsed_html: html.HtmlElement = html.fromstring(response.content)
        return parsed_html
