from fastapi.testclient import TestClient
from ORM.main import app
import pytest

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ORM.config import settings
from ORM.database import get_db
from ORM.database import Base
from alembic import command

#  Connecting to the database
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

# creating an engine - what's responsible for sqlalchemy to connect to a postgres database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL)

# session - used to talk to the sql database
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


# Base.metadata.create_all(bind=engine)

# def override_get_db():
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# app.dependency_overrides[get_db] = override_get_db


# setting our test client to a variable called client
# client = TestClient(app)


# fixture that returns our database object
@pytest.fixture(scope="function")
def session():
    print("My session fixture ran")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Fixture that returns our client
@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
