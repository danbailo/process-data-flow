import time

import schedule

from process_data_flow.services.product import SendProductsToRabbitService

if __name__ == '__main__':
    send_products_to_rabbit = SendProductsToRabbitService()

    schedule.every(10).seconds.do(send_products_to_rabbit.execute)

    while True:
        schedule.run_pending()
        time.sleep(1)
