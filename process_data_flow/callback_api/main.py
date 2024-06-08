from fastapi import FastAPI

from process_data_flow.callback_api.utils import generate_random_data

app = FastAPI()


@app.get('/items')
async def check_if_have_items():
    items_to_return = generate_random_data()
    return {'size': len(items_to_return), 'items': items_to_return}


@app.get('/health')
async def health():
    return {'detail': 'ok'}
