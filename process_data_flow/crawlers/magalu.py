import httpx

from process_data_flow.commons.decorators import async_cache
from process_data_flow.commons.requests import MethodRequestEnum, make_async_request
from process_data_flow.crawlers.base import BaseCrawler
from process_data_flow.settings import (
    REDIS_CACHE_TTL,
)


class MagaluCrawler(BaseCrawler):
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

    def _extract_data_from_first_page(self, response: httpx.Response) -> list[str]:
        to_return = []

        page_html = self.build_html(response)
        elements = page_html.xpath('//div[@data-testid="product-list"]//li')

        for element in elements:
            href = element.xpath('./a')[0].get('href')
            to_return.append(href)

        self.logger.info('Data extracted!', data=dict(elements=len(to_return)))
        return to_return

    def _extract_product_data_from_url(self, response: httpx.Response) -> dict:
        page_html = self.build_html(response)

        name = page_html.xpath('//h1[@data-testid="heading-product-title"]/text()')[0]
        price = page_html.xpath(
            '//div[@data-testid="product-price"]//p[@data-testid="price-value"]/text()'
        )[0]
        if seller := page_html.xpath('//div[@href="/lojista/"]/p/label//text()'):
            seller = seller[0]
        else:
            seller = page_html.xpath(
                '//div[@href="/lojista/"]/p/*[@data-testid="magalogo"]'
            )
            if seller and seller[0].tag:
                seller = 'Magalu'
            else:
                seller = ''
        infos = page_html.xpath(
            '//div[@data-testid="product-detail-description"]//text()'
        )
        code = page_html.xpath(
            '//h1[@data-testid="heading-product-title"]'
            '/following-sibling::span/span/text()[last()]'
        )[0]

        return {
            'name': name,
            'price': price,
            'seller': seller,
            'infos': infos or None,
            'code': code,
        }

    @async_cache(ttl=REDIS_CACHE_TTL, is_class_method=True)
    async def get_products_from_first_page(self, product: str):
        self.logger.info(
            'Getting products from first page...', data=dict(product=product)
        )

        url = self.base_url + f'/busca/{product}/?from=submit'
        first_page_product_response = await make_async_request(
            MethodRequestEnum.GET, url, headers=self.headers
        )
        extract_data = self._extract_data_from_first_page(first_page_product_response)

        return extract_data

    @async_cache(ttl=REDIS_CACHE_TTL, is_class_method=True)
    async def extract_data_from_product(self, url: str):
        self.logger.info('Extracting data from product url', data=dict(url=url))

        product_page_response = await make_async_request(
            MethodRequestEnum.GET, url, headers=self.headers
        )
        data = self._extract_product_data_from_url(product_page_response)

        return data
