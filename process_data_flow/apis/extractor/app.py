from fastapi import FastAPI

from process_data_flow.apis.extractor.routers import extract_data, monitor, product

app = FastAPI(title='Extractor API')


@app.get('/health')
async def health():
    return {'detail': 'ok'}


app.include_router(extract_data.route, prefix='/extract-data', tags=['extract-data'])
app.include_router(monitor.route, prefix='/monitor', tags=['monitor'])
app.include_router(product.route, prefix='/product', tags=['product'])
