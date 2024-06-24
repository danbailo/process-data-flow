from process_data_flow.commons.logger import Logger, LoggerFactory


class FormatExtractedUrlService:
    def __init__(self, logger: Logger = LoggerFactory.new()):
        self.logger = logger

    def _format_extracted_url(self, extracted_url: str) -> dict:
        base_url = 'https://www.magazineluiza.com.br'
        extracted_url = extracted_url.strip('"')

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


class FormatExtractedDataFromUrlService:
    def __init__(self, logger: Logger = LoggerFactory.new()):
        self.logger = logger

    def _format_price_value(self, value: str) -> float:
        value_to_return = value.strip().encode('ascii', 'ignore').decode()
        value_to_return = value_to_return.removeprefix('R$').replace(',', '.')
        return float(value_to_return)

    def _format_extracted_data_from_url(self, extracted_data: dict) -> dict:
        price = self._format_price_value(extracted_data['price'])
        infos = '\n'.join(extracted_data['infos']) if extracted_data['infos'] else None
        data = {
            'name': extracted_data['name'].strip(),
            'price': price,
            'seller': extracted_data['seller'].strip(),
            'infos': infos,
            'code': extracted_data['code'].strip(),
        }
        return data

    def execute(self, data: dict) -> dict:
        self.logger.info('Executing Format Extracted Data from url Service...')

        formatted_data = self._format_extracted_data_from_url(data)
        self.logger.info(
            'Extracted data from url formatted!', data=dict(formatted_data=data)
        )

        return formatted_data
