import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

os.environ["ENV_STATE"] = "test"

from socialmediaapi.database import database, users_table  # noqa: E402
from socialmediaapi.main import app  # noqa: E402


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=client.base_url
    ) as ac:
        yield ac


@pytest.fixture
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@example.com", "password": "1234"}
    await async_client.post("/register", json=user_details)
    query = users_table.select().where(users_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user.id
    return user_details


@pytest.fixture
async def confirmed_user(async_client: AsyncClient, registered_user: dict) -> dict:
    query = (
        users_table.update()
        .where(users_table.c.email == registered_user["email"])
        .values(confirmed=True)
    )
    await database.execute(query)
    return registered_user


@pytest.fixture
async def logged_in_token(async_client: AsyncClient, confirmed_user: dict):
    response = await async_client.post(
        "/token",
        data={
            "username": confirmed_user["email"],
            "password": confirmed_user["password"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return response.json()["access_token"]
