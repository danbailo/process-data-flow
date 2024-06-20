import redis
from sqlmodel import Session

from process_data_flow.apis.database import engine
from process_data_flow.settings import REDIS_CONNECTION_POOL


def get_redis_client():
    return redis.Redis(connection_pool=REDIS_CONNECTION_POOL)


def get_session():
    with Session(engine) as session:
        yield session
