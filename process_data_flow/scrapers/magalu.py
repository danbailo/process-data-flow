import httpx
from lxml import html
from tenacity import retry, stop_after_attempt, wait_fixed

from process_data_flow.commons.decorators import async_cache
from process_data_flow.commons.requests import MethodRequestEnum, make_async_request
from process_data_flow.commons.tenacity import warning_if_failed
from process_data_flow.scrapers.base import BaseScraper
from process_data_flow.settings import (
    REDIS_CACHE_TTL,
    RETRY_AFTER_SECONDS,
    RETRY_ATTEMPTS,
)


class MagaluScraper(BaseScraper):
    @property
    def base_url(self):
        return 'https://www.magazineluiza.com.br'

    @property
    def headers(self):
        return {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }

    @retry(
        reraise=True,
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_fixed(RETRY_AFTER_SECONDS),
        before=warning_if_failed,
    )
    async def _search_by_product(self, product: str) -> httpx.Response:
        url = self.base_url + f'/busca/{product}/?from=submit'
        response = await make_async_request(
            MethodRequestEnum.GET, url, headers=self.headers
        )
        return response

    def _extract_data_from_first_page(
        self, elements: list[html.HtmlElement]
    ) -> list[str]:
        to_return = []

        for element in elements:
            href = element.xpath('./a')[0].get('href')
            to_return.append(href)

        self.logger.info('Data extracted!')
        return to_return

    @async_cache(ttl=REDIS_CACHE_TTL, is_class_method=True)
    async def get_products_from_first_page(self, product: str):
        self.logger.info(
            'Getting products from first page...', data=dict(product=product)
        )

        response = await self._search_by_product(product)
        xpath = '//div[@data-testid="product-list"]//li'
        elements = self.get_elements_from_page(response, xpath)
        extract_data = self._extract_data_from_first_page(elements)

        return extract_data

    @async_cache(ttl=REDIS_CACHE_TTL, is_class_method=True)
    async def extract_data_from_product(self, url):
        self.logger.info('Extracting data from product url', data=dict(url=url))

        response = await make_async_request(
            MethodRequestEnum.GET, url, headers=self.headers
        )
        element = self.build_html(response)

        return {
            'name': element.xpath('//h1[@data-testid="heading-product-title"]')[
                0
            ].text.strip(),
            'code': element.xpath(
                '//h1[@data-testid="heading-product-title"]/following-sibling::span/span/text()[last()]'
            )[0],
            'price': element.xpath(
                '//div[@data-testid="product-price"]//p[@data-testid="price-value"]'
            )[0].text.strip(),
            'seller': element.xpath('//div[@href="/lojista/"]/p/label')[0].text.strip(),
            'infos': element.xpath(
                '//div[@data-testid="product-detail-description"]/div'
            )[0].text.strip(),
        }
