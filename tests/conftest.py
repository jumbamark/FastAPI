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
from ORM.oauth2 import create_access_token
from ORM import models

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


# creating a test user for login_user test
@pytest.fixture
def test_user(client):
    user_data = {"email": "allie@gmail.com", "password": "allie"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    print(res.json())
    # return
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email": "nonnie@gmail.com", "password": "nonnie"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    print(res.json())
    # return
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


# Fixture that creates a post
@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [
        {
            "title": "Life Lesson 1",
            "content": "Be ROMANTIC",
            "owner_id": test_user["id"]
        },
        {
            "title": "Life Lesson 3",
            "content": "Count your BLESSINGS",
            "owner_id": test_user["id"]
        },
        {
            "title": "Life Lesson 5",
            "content": "Don't EXPECT life to be FAIR",
            "owner_id": test_user["id"]
        },
        {
            "title": "Life Lesson 11",
            "content": "Whistle",
            "owner_id": test_user2["id"]
        }
    ]

    # session.add_all([
    #     models.Post(title="Life Lesson 1", content="Be ROMANTIC",owner_id=test_user["id"]),
    #     models.Post(title="Life Lesson 3",content="Count your BLESSINGS", owner_id=test_user["id"]),
    #     models.Post(title="Life Lesson 5",content="Don't EXPECT life to be FAIR", owner_id=test_user["id"]),
    # ])
    # session.commit()
    # session.query(models.Post).all()

    # using the map function
    def create_posts_model(post):
        return models.Post(**post)

    post_map = map(create_posts_model, posts_data)
    posts = list(post_map)
    session.add_all(posts)
    session.commit()
    posts = session.query(models.Post).all()
    return posts
