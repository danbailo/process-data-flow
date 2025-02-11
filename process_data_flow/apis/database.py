from sqlmodel import SQLModel, create_engine

from process_data_flow.settings import DATABASE_URL

engine = create_engine(
    DATABASE_URL, echo=True, connect_args={'check_same_thread': False}
)


def init_db():
    SQLModel.metadata.create_all(engine)
