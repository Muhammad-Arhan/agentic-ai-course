"""Client for the external API.

This is the only place that talks HTTP to the outside world. It:
  * sends requests with a timeout (never wait forever),
  * adds the Authorization header when an API key is configured,
  * turns every failure into a clear, specific Python exception,
    so the rest of the application never has to look at raw status codes.
"""

import logging

import requests

from api_service.config import EXTERNAL_API_BASE_URL, EXTERNAL_API_KEY, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Exceptions: one per kind of failure (Phase 05: errors, timeouts, rate limits)
# --------------------------------------------------------------------------- #
class ExternalApiError(Exception):
    """Base class for every failure while calling the external API."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class BadRequestError(ExternalApiError):
    """400: the external API rejected our request."""


class UnauthorizedError(ExternalApiError):
    """401: missing or invalid credentials."""


class ForbiddenError(ExternalApiError):
    """403: credentials are valid but access is not allowed."""


class NotFoundError(ExternalApiError):
    """404: the requested resource does not exist."""


class RateLimitError(ExternalApiError):
    """429: too many requests. `retry_after` is seconds to wait, if provided."""

    def __init__(self, message, status_code=429, retry_after=None):
        super().__init__(message, status_code)
        self.retry_after = retry_after


class ServerError(ExternalApiError):
    """5xx: the external API failed."""


class ApiTimeoutError(ExternalApiError):
    """No response within the timeout."""


class ApiConnectionError(ExternalApiError):
    """Network failure: DNS, refused connection, dropped connection..."""


class InvalidResponseError(ExternalApiError):
    """The API answered, but not with the data we expected (e.g. invalid JSON)."""


# --------------------------------------------------------------------------- #
# The client
# --------------------------------------------------------------------------- #
class ExternalApiClient:
    def __init__(self, base_url=None, api_key=None, timeout=None, session=None):
        self.base_url = (base_url or EXTERNAL_API_BASE_URL).rstrip("/")
        self.api_key = api_key if api_key is not None else EXTERNAL_API_KEY
        self.timeout = timeout if timeout is not None else REQUEST_TIMEOUT
        self.session = session or requests.Session()

    # -- public helpers: HTTP method + path -> parsed JSON ------------------- #
    def get(self, path, params=None):
        return self._request("GET", path, params=params)

    def post(self, path, json=None):
        return self._request("POST", path, json=json)

    def put(self, path, json=None):
        return self._request("PUT", path, json=json)

    def delete(self, path):
        return self._request("DELETE", path)

    # -- internals ----------------------------------------------------------- #
    def _headers(self):
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _request(self, method, path, **kwargs):
        url = f"{self.base_url}/{path.lstrip('/')}"
        logger.info("External API request: %s %s", method, url)

        try:
            response = self.session.request(
                method, url, headers=self._headers(), timeout=self.timeout, **kwargs
            )
        except requests.Timeout as exc:  # must come before ConnectionError
            logger.error("Timeout after %s seconds: %s %s", self.timeout, method, url)
            raise ApiTimeoutError(
                f"No response from the external API within {self.timeout} seconds."
            ) from exc
        except requests.ConnectionError as exc:
            logger.error("Connection failure: %s %s", method, url)
            raise ApiConnectionError("Could not connect to the external API.") from exc
        except requests.RequestException as exc:
            logger.error("Request failure: %s %s (%s)", method, url, exc)
            raise ApiConnectionError("The request to the external API failed.") from exc

        return self._handle_response(response, method, url)

    def _handle_response(self, response, method, url):
        status = response.status_code

        if 200 <= status < 300:
            if status == 204 or not response.content:
                return None
            try:
                return response.json()
            except ValueError as exc:
                raise InvalidResponseError(
                    "The external API returned invalid JSON.", status
                ) from exc

        # HTTP response received != operation succeeded (Phase 05).
        logger.warning("External API error %s for %s %s", status, method, url)

        if status == 400:
            raise BadRequestError("The external API rejected the request.", status)
        if status == 401:
            raise UnauthorizedError("The external API rejected our credentials.", status)
        if status == 403:
            raise ForbiddenError("Access to the external API resource is forbidden.", status)
        if status == 404:
            raise NotFoundError("Resource not found.", status)
        if status == 429:
            raise RateLimitError(
                "The external API rate limit was exceeded.",
                status,
                retry_after=self._parse_retry_after(response),
            )
        if status >= 500:
            raise ServerError("The external API failed.", status)
        raise ExternalApiError(f"Unexpected response from the external API ({status}).", status)

    @staticmethod
    def _parse_retry_after(response):
        """Retry-After is usually a number of seconds; ignore any other format."""
        value = response.headers.get("Retry-After")
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
