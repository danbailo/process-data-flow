import time

import schedule

from process_data_flow.commons.logger import LoggerFactory
from process_data_flow.repositories.product import ProductRepository
from process_data_flow.services.product import SendProductsToRabbitService

if __name__ == '__main__':
    logger = LoggerFactory.new()
    product_repository = ProductRepository(logger=logger)
    send_products_to_rabbit = SendProductsToRabbitService(
        product_repository, logger=logger
    )

    schedule.every(10).seconds.do(send_products_to_rabbit.execute)

    while True:
        schedule.run_pending()
        time.sleep(1)
