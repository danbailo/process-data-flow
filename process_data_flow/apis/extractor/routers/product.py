from fastapi import APIRouter

from process_data_flow.utils import random_generate_fake_products

route = APIRouter(prefix='/product', tags=['product'])


@route.get('')
async def check_if_have_products():
    products_to_return = random_generate_fake_products()
    return {'size': len(products_to_return), 'products': products_to_return}
