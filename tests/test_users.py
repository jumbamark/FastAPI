from ORM import schemas
# from .database import client, session
import pytest
from jose import jwt
from ORM.config import settings


def test_root(client):
    res = client.get("/")
    # print(res)
    print(res.json())
    # print(res.json().get("message"))
    assert res.json().get(
        "message") == "Welcome to my API, here's to excellent stuff: bind mount works fine"
    assert res.status_code == 200


# testing the user create functionality
def test_create_user(client):
    res = client.post(
        "/users/", json={"email": "gathoni@gmail.com", "password": "gathoni"})
    print(res.json().get("email")) == "gathoni@gmail.com"
    assert res.json().get("email") == "gathoni@gmail.com"

    # confirm do we have what's in UserOut
    new_user = schemas.UserOut(**res.json())
    assert new_user.email == "gathoni@gmail.com"

    assert res.status_code == 201


def test_login_user(client, test_user):
    res = client.post(
        "/login", data={"username": test_user["email"], "password": test_user["password"]})
    # print(res.json())
    login_res = schemas.Token(**res.json())
    # valid the token - logic used within our auth2.py file (decode to make user user id is within that token)
    payload = jwt.decode(login_res.access_token,
                         settings.secret_key, algorithms=[settings.algorithm])
    id: str = payload.get("user_id")
    assert id == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize("email, password, status_code", [
    ("wrongemail@gmail.com", "allie", 403),
    ("allie@gmail.com", "wrongPassword", 403),
    ("wrongemail@gmail.com", "wrongPassword", 403),
    (None, "allie", 422),
    ("allie@gmail.com", None, 422)
])
def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post(
        "/login", data={"username": email, "password": password})
    assert res.status_code == status_code
    # assert res.json().get("detail") == "Invalid credentials"
