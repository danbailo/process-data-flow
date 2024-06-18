from fastapi import APIRouter, BackgroundTasks

route = APIRouter(prefix='/extract-data', tags=['extract-data'])


@route.get('/start')
async def extract_data_from_monitored_products():
    pass


@route.get('/start/{product}')
async def extract_data_from_product(product: str, background_tasks: BackgroundTasks):
    background_tasks.add_task()
    pass
