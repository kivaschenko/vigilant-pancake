import time

import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.orm import metadata, start_mappers, clear_mappers
from config import Settings

settings = Settings()


def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("Postgres never came up")


@pytest.fixture(scope="session")
def postgres_db():
    engine = create_engine(settings.DATABASE_URL)
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session(postgres_db):
    start_mappers()
    connection = postgres_db.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
    clear_mappers()


@pytest.fixture(autouse=True)
def clean_database(postgres_db):
    """Clean up the database after each test"""
    metadata.drop_all(postgres_db)
    metadata.create_all(postgres_db)
