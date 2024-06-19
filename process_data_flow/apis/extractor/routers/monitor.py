from fastapi import APIRouter

router = APIRouter(prefix='/monitor', tags=['monitor'])


@router.get('/products')
async def show_monitored_products():
    pass


@router.post('/products')
async def monitor_new_product():
    pass


@router.delete('/products')
async def remove_product():
    pass
