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

    def _prepare_payload(self, data: dict):
        data = {
            'entry.21246675': 'in code',
            'entry.1536952958': 'asdasd',
            'entry.2116193397': 'test',
            'entry.430735533': 'asdasd',
            'entry.283464321_year': '2024',
            'entry.283464321_month': '6',
            'entry.283464321_day': '29',
        }
        return data

    async def _access_form_page(self) -> Response:
        url = (
            self.base_url
            + '/forms/d/e/1FAIpQLScAY0_xbg2kswQjY9OdB3E4TUaQMGFYbEatiPcVSPY_udmqgg/viewform?usp=sf_link'
        )
        response = await self.client.get(url)
        return response

    async def submit_form(self):
        action = '/forms/u/0/d/e/1FAIpQLScAY0_xbg2kswQjY9OdB3E4TUaQMGFYbEatiPcVSPY_udmqgg/formResponse'
        url = self.base_url + action
        data = self._prepare_payload({})
        response = await self.client.post(
            url,
            data=data,
        )
        if not regex.search(r'registrad', response.text, flags=regex.I):
            raise Exception()

        self.logger.info('Product registered with sucessfully!')
