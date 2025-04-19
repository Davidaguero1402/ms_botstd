# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope="module")
def engine() -> Engine:
    database_url = os.getenv("DATABASE_URL")  # Debe estar en tu .env
    return create_engine(database_url)

@pytest.fixture(scope="module")
def connection(engine):
    with engine.connect() as connection:
        yield connection
