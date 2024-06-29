import dateparser
import regex
from httpx import Response

from process_data_flow.crawlers.base import BaseCrawler


class RegisterProductCrawler(BaseCrawler):
    @property
    def base_url(self):
        return 'https://docs.google.com'

    @property
    def headers(self):
        return {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'pt-BR,pt;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-full-version-list': '"Not/A)Brand";v="8.0.0.0", "Chromium";v="126.0.6478.126", "Google Chrome";v="126.0.6478.126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Linux"',
            'sec-ch-ua-platform-version': '"5.15.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }

    def _prepare_payload(self, data: dict) -> dict:
        created_at = dateparser.parse(data['created_at'])
        payload = {
            'entry.21246675': data['name'],
            'entry.1536952958': data['price'],
            'entry.2116193397': data['seller'],
            'entry.430735533': data['infos'],
            'entry.283464321_year': created_at.year,
            'entry.283464321_month': created_at.month,
            'entry.283464321_day': created_at.day,
        }
        self.logger.debug('Payload prepared.', payload=payload)
        return payload

    async def _access_form_page(self) -> Response:
        url = (
            self.base_url
            + '/forms/d/e/1FAIpQLScAY0_xbg2kswQjY9OdB3E4TUaQMGFYbEatiPcVSPY_udmqgg/viewform?usp=sf_link'
        )
        response = await self.client.get(url)
        self.logger.info('Accessed form page.')
        return response

    async def submit_form(self, data: dict):
        self.logger.info('Submitting form...')
        url = (
            self.base_url
            + '/forms/u/0/d/e/1FAIpQLScAY0_xbg2kswQjY9OdB3E4TUaQMGFYbEatiPcVSPY_udmqgg/formResponse'
        )
        payload = self._prepare_payload(data)
        response = await self.client.post(
            url,
            data=payload,
        )
        if not regex.search(r'registrad', response.text, flags=regex.I):
            raise Exception("It wasn't possible to register the product!")

        self.logger.info(
            'Product registered with sucessfully!', data=dict(product=data)
        )
