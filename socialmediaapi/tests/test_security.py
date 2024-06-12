from typing import Callable

import pytest
from jose import jwt

from socialmediaapi import security


def test_access_token_expire_minutes():
    assert security.access_token_expire_minutes() == 30


def test_confirmation_token_expire_minutes():
    assert security.confirmation_token_expire_minutes() == 1440


def test_create_access_token():
    token = security.create_access_token("123")
    assert {"sub": "123", "type": "access"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


def test_create_confirmation_token():
    token = security.create_confirmation_token("123")
    assert {"sub": "123", "type": "confirmation"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


@pytest.mark.parametrize(
    "create_token_func, token_type",
    [
        (security.create_confirmation_token, "confirmation"),
        (security.create_access_token, "access"),
    ],
)
def test_get_subject_for_token_type_valid(create_token_func: Callable, token_type: str):
    email = "test@example.com"
    token = create_token_func(email)
    assert email == security.get_subject_for_token_type(token, token_type)


def test_get_subject_for_token_type_expirer(mocker):
    mocker.patch("socialmediaapi.security.access_token_expire_minutes", return_value=-1)
    email = "test@example.com"
    token = security.create_access_token(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
    assert "Token has expired" == exc_info.value.detail


def test_get_subject_for_token_type_invalid_token(mocker):
    token = "Invalid token"
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
    assert "Invalid token" == exc_info.value.detail


def test_get_subject_for_token_type_missing_sub(mocker):
    email = "test@example.com"
    token = security.create_access_token(email)
    payload = jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    )
    del payload["sub"]
    token = jwt.encode(payload, key=security.SECRET_KEY, algorithm=security.ALGORITHM)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
    assert "Token is missing 'sub' field" == exc_info.value.detail


@pytest.mark.parametrize(
    "create_token_func, token_type",
    [
        (security.create_confirmation_token, "access"),
        (security.create_access_token, "confirmation"),
    ],
)
def test_get_subject_for_token_type_wrong_type(
    create_token_func: Callable, token_type: str
):
    email = "test@example.com"
    token = create_token_func(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, token_type)
    assert "Token has incorrect type" in exc_info.value.detail


def test_password_hashed():
    password = "password"
    hashed_password = security.get_password_hash(password)
    assert security.verify_password(password, hashed_password)


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    user = await security.get_user(registered_user["email"])

    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found():
    user = await security.get_user("test@example.com")

    assert user is None


@pytest.mark.anyio
async def authenticate_user(registered_user: dict):
    user = await security.authenticate_user(
        registered_user["email"], registered_user["password"]
    )
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def authenticate_user_not_found():
    with pytest.raises(security.HTTPException):
        await security.authenticate_user("test@example.com", "123456")


@pytest.mark.anyio
async def authenticate_user_wrong_password(registered_user: dict):
    with pytest.raises(security.HTTPException):
        await security.authenticate_user(registered_user["email"], "wrong")


@pytest.mark.anyio
async def get_current_user(registered_user: dict):
    token = security.create_access_token(email=registered_user["email"])
    user = await security.get_current_user(token)
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def get_current_user_invalid_token(registered_user: dict):
    with pytest.raises(security.HTTPException):
        await security.get_current_user("invalidtoken")


@pytest.mark.anyio
async def get_current_user_wrong_type_token(registered_user: dict):
    token = security.create_confirmation_token(email=registered_user["email"])
    with pytest.raises(security.HTTPException):
        await security.get_current_user(token)
