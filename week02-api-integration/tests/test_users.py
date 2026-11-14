import pytest

from api_service.clients.external_api import (
    ApiConnectionError,
    ApiTimeoutError,
    InvalidResponseError,
    RateLimitError,
    ServerError,
    UnauthorizedError,
)

VALID_USER = {"name": "Ali Khan", "username": "ali", "email": "ali@example.com"}


# ---- the five REST operations -------------------------------------------- #
def test_list_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    users = response.json()
    assert [u["id"] for u in users] == [1, 2]
    # Only our own fields are exposed (no phone/address leaking through).
    assert set(users[0]) == {"id", "name", "username", "email"}


def test_get_user(client):
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Leanne Graham"


def test_create_user(client):
    response = client.post("/users", json=VALID_USER)
    assert response.status_code == 201
    assert response.json() == {"id": 11, **VALID_USER}


def test_update_user(client):
    response = client.put("/users/1", json=VALID_USER)
    assert response.status_code == 200
    assert response.json() == {"id": 1, **VALID_USER}


def test_delete_user(client):
    response = client.delete("/users/1")
    assert response.status_code == 204
    assert response.content == b""


# ---- our own input validation (422) -------------------------------------- #
def test_create_user_rejects_missing_field(client):
    response = client.post("/users", json={"name": "Ali"})
    assert response.status_code == 422


def test_create_user_rejects_invalid_email(client):
    response = client.post("/users", json={**VALID_USER, "email": "not-an-email"})
    assert response.status_code == 422


def test_create_user_rejects_empty_name(client):
    response = client.post("/users", json={**VALID_USER, "name": ""})
    assert response.status_code == 422


def test_user_id_must_be_a_positive_number(client):
    assert client.get("/users/abc").status_code == 422
    assert client.get("/users/0").status_code == 422


# ---- failures of the external API are translated, never leaked ------------ #
def test_unknown_user_returns_404(client):
    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Resource not found."}


def test_update_unknown_user_returns_404(client):
    assert client.put("/users/999", json=VALID_USER).status_code == 404


def test_delete_unknown_user_returns_404(client):
    assert client.delete("/users/999").status_code == 404


def test_rate_limit_returns_429_with_retry_after(client, fake_client):
    fake_client.error = RateLimitError("limit", retry_after=30)
    response = client.get("/users")
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "30"


def test_rate_limit_without_retry_after_header(client, fake_client):
    fake_client.error = RateLimitError("limit")
    response = client.get("/users")
    assert response.status_code == 429
    assert "Retry-After" not in response.headers


def test_timeout_returns_504(client, fake_client):
    fake_client.error = ApiTimeoutError("slow")
    assert client.get("/users").status_code == 504


@pytest.mark.parametrize(
    "error",
    [
        ApiConnectionError("down"),
        ServerError("boom", 500),
        UnauthorizedError("bad key", 401),
        InvalidResponseError("garbage"),
    ],
)
def test_other_upstream_failures_return_502(client, fake_client, error):
    fake_client.error = error
    response = client.get("/users")
    assert response.status_code == 502
    # No stack trace or internal details are exposed.
    assert set(response.json()) == {"detail"}


def test_unexpected_upstream_data_returns_502(client, fake_client):
    fake_client.users[1] = {"unexpected": "shape"}
    assert client.get("/users/1").status_code == 502
