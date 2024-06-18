import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')

CALLBACK_API_URL = os.getenv('CALLBACK_API_URL', 'http://localhost:8081')
MARKET_API_URL = os.getenv('MARKET_API_URL', 'http://localhost:8082')

RABBITMQ_HOST = os.getenv('RABBIT_HOST', 'localhost')

RETRY_ATTEMPTS = 7
RETRY_AFTER_SECONDS = 3

MESSAGE_TTL = 300000

PRODUCT_CONSUMER_EXCHANGE = 'product_consumer.exchange'
PRODUCT_CONSUMER_QUEUE = 'product_consumer.queue'
PRODUCT_CONSUMER_KEY = 'product_consumer_key'

MARKET_QUERY_EXCHANGE = 'market_query.exchange'
MARKET_QUERY_QUEUE = 'market_query.queue'
MARKET_QUERY_KEY = 'market_query_key'
MARKET_QUERY_DLX = 'market_query.dlx'
MARKET_QUERY_DLQ = 'market_query.dlq'
MARKET_QUERY_DL_KEY = 'market_query_dl_key'

REGISTER_PRODUCT_EXCHANGE = 'register_product.exchange'
REGISTER_PRODUCT_QUEUE = 'register_product.queue'
REGISTER_PRODUCT_KEY = 'register_product_key'
REGISTER_PRODUCT_DLX = 'register_product.dlx'
REGISTER_PRODUCT_DLQ = 'register_product.dlq'
REGISTER_PRODUCT_DL_KEY = 'register_product_dl_key'
