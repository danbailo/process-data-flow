from fastapi import FastAPI

from process_data_flow.utils import random_generate_fake_products

app = FastAPI()


@app.get('/products')
async def check_if_have_products():
    products_to_return = random_generate_fake_products()
    return {'size': len(products_to_return), 'products': products_to_return}


@app.get('/health')
async def health():
    return {'detail': 'ok'}
