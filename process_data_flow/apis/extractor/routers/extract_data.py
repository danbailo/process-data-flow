from fastapi import APIRouter

route = APIRouter()


@route.get('/start')
async def extract_data_from_monitored_products():
    pass


@route.get('/start/{product}')
async def extract_data_from_product():
    pass
