import time

from process_data_flow.commons.mp_scheduler import MPScheduler
from process_data_flow.services.extract_data import SendExtractedDataService

if __name__ == '__main__':
    mp_sched = MPScheduler()

    mp_sched.every(10).seconds.do(SendExtractedDataService().execute)

    while True:
        mp_sched.run_pending()
        time.sleep(1)
