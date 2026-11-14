"""Tests for the external API client, using a fake HTTP session (no internet)."""

import pytest
import requests

from api_service.clients.external_api import (
    ApiConnectionError,
    ApiTimeoutError,
    BadRequestError,
    ExternalApiClient,
    ExternalApiError,
    ForbiddenError,
    InvalidResponseError,
    NotFoundError,
    RateLimitError,
    ServerError,
    UnauthorizedError,
)


def make_response(status_code=200, body=b"{}", headers=None):
    response = requests.Response()
    response.status_code = status_code
    response._content = body
    response.headers.update(headers or {})
    return response


class FakeSession:
    """Records the request and returns a canned response or raises an error."""

    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, **kwargs})
        if self.error is not None:
            raise self.error
        return self.response


def make_client(response=None, error=None, **kwargs):
    session = FakeSession(response, error)
    client = ExternalApiClient(base_url="https://api.test", session=session, **kwargs)
    return client, session


# ---- success -------------------------------------------------------------- #
def test_get_returns_parsed_json():
    client, session = make_client(make_response(200, b'{"id": 1}'))
    assert client.get("/posts/1") == {"id": 1}
    assert session.calls[0]["method"] == "GET"
    assert session.calls[0]["url"] == "https://api.test/posts/1"


def test_204_returns_none():
    client, _ = make_client(make_response(204, b""))
    assert client.delete("/posts/1") is None


def test_post_sends_json_body():
    client, session = make_client(make_response(201, b'{"id": 101}'))
    client.post("/posts", json={"title": "x"})
    assert session.calls[0]["json"] == {"title": "x"}


# ---- timeout is always set ------------------------------------------------ #
def test_timeout_is_always_sent():
    client, session = make_client(make_response(), timeout=7)
    client.get("/posts/1")
    assert session.calls[0]["timeout"] == 7


def test_default_timeout_is_set():
    client, session = make_client(make_response())
    client.get("/posts/1")
    assert session.calls[0]["timeout"] is not None


# ---- authentication header ------------------------------------------------ #
def test_bearer_header_added_when_key_configured():
    client, session = make_client(make_response(), api_key="secret-123")
    client.get("/posts/1")
    assert session.calls[0]["headers"]["Authorization"] == "Bearer secret-123"


def test_no_authorization_header_without_key():
    client, session = make_client(make_response(), api_key="")
    client.get("/posts/1")
    assert "Authorization" not in session.calls[0]["headers"]


# ---- HTTP status codes -> exceptions ------------------------------------- #
@pytest.mark.parametrize(
    "status, expected",
    [
        (400, BadRequestError),
        (401, UnauthorizedError),
        (403, ForbiddenError),
        (404, NotFoundError),
        (429, RateLimitError),
        (500, ServerError),
        (502, ServerError),
        (503, ServerError),
        (418, ExternalApiError),
    ],
)
def test_error_status_codes_raise_specific_exceptions(status, expected):
    client, _ = make_client(make_response(status, b"{}"))
    with pytest.raises(expected) as info:
        client.get("/anything")
    assert info.value.status_code == status


def test_429_reads_retry_after_seconds():
    client, _ = make_client(make_response(429, b"{}", {"Retry-After": "12"}))
    with pytest.raises(RateLimitError) as info:
        client.get("/anything")
    assert info.value.retry_after == 12


def test_429_ignores_unparseable_retry_after():
    client, _ = make_client(make_response(429, b"{}", {"Retry-After": "tomorrow"}))
    with pytest.raises(RateLimitError) as info:
        client.get("/anything")
    assert info.value.retry_after is None


def test_invalid_json_raises():
    client, _ = make_client(make_response(200, b"<html>not json</html>"))
    with pytest.raises(InvalidResponseError):
        client.get("/anything")


# ---- failures where no response arrives ---------------------------------- #
def test_timeout_raises_api_timeout_error():
    client, _ = make_client(error=requests.Timeout("slow"))
    with pytest.raises(ApiTimeoutError):
        client.get("/anything")


def test_connect_timeout_is_treated_as_timeout():
    client, _ = make_client(error=requests.ConnectTimeout("slow"))
    with pytest.raises(ApiTimeoutError):
        client.get("/anything")


def test_connection_error_raises_api_connection_error():
    client, _ = make_client(error=requests.ConnectionError("dns"))
    with pytest.raises(ApiConnectionError):
        client.get("/anything")


def test_other_request_errors_raise_api_connection_error():
    client, _ = make_client(error=requests.exceptions.InvalidURL("bad"))
    with pytest.raises(ApiConnectionError):
        client.get("/anything")
