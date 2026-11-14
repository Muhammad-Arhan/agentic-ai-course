"""Shared test helpers: a fake external client so tests never touch the internet."""

import pytest
from fastapi.testclient import TestClient

from api_service.clients.external_api import NotFoundError
from api_service.main import app
from api_service.routes.users import get_user_service
from api_service.services.user_service import UserService

SAMPLE_USERS = {
    1: {"id": 1, "name": "Leanne Graham", "username": "Bret", "email": "Sincere@april.biz",
        "phone": "1-770-736-8031", "address": {"city": "Gwenborough"}},
    2: {"id": 2, "name": "Ervin Howell", "username": "Antonette", "email": "Shanna@melissa.tv"},
}


class FakeExternalClient:
    """Behaves like ExternalApiClient, but serves canned data from memory.

    Set `fake.error = SomeExternalApiError(...)` to make every call fail.
    """

    def __init__(self):
        self.users = {k: dict(v) for k, v in SAMPLE_USERS.items()}
        self.error = None
        self.calls = []

    def _check(self, method, path):
        self.calls.append((method, path))
        if self.error is not None:
            raise self.error

    def _user_id(self, path):
        return int(path.rsplit("/", 1)[1])

    def get(self, path, params=None):
        self._check("GET", path)
        if path == "/users":
            return list(self.users.values())
        user_id = self._user_id(path)
        if user_id not in self.users:
            raise NotFoundError("Resource not found.", 404)
        return self.users[user_id]

    def post(self, path, json=None):
        self._check("POST", path)
        return {**json, "id": 11}

    def put(self, path, json=None):
        self._check("PUT", path)
        user_id = self._user_id(path)
        if user_id not in self.users:
            raise NotFoundError("Resource not found.", 404)
        return {**json, "id": user_id}

    def delete(self, path):
        self._check("DELETE", path)
        user_id = self._user_id(path)
        if user_id not in self.users:
            raise NotFoundError("Resource not found.", 404)
        return {}


@pytest.fixture
def fake_client():
    return FakeExternalClient()


@pytest.fixture
def client(fake_client):
    """A TestClient whose UserService uses the fake external client."""
    app.dependency_overrides[get_user_service] = lambda: UserService(fake_client)
    yield TestClient(app)
    app.dependency_overrides.clear()
