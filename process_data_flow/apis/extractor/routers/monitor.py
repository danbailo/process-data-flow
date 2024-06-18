from fastapi import APIRouter

route = APIRouter(prefix='/monitor', tags=['monitor'])


@route.get('/products')
async def show_monitored_products():
    pass


@route.post('/products')
async def monitor_new_product():
    pass


@route.delete('/products')
async def remove_product():
    pass
