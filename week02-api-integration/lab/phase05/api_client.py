"""Phase 05 - Tasks 19-22: errors, timeouts and rate limits.

One function, call_api(), always returns a result dictionary instead of
crashing. Each result has a "kind":

    success        - the API answered with a 2xx status
    api_error      - the API answered, but with an error status (400, 401, 404, 429, 500...)
    timeout        - no answer within the timeout
    network_error  - we could not reach the API at all

Remember: HTTP response received != requested operation succeeded.

Run from the week02-api-integration folder:
    python lab/phase05/api_client.py
"""

import time

import requests

TIMEOUT = 10  # seconds: the maximum time we are willing to wait

STATUS_MESSAGES = {
    400: "Bad request. The server could not understand the request.",
    401: "Unauthorized. Credentials are missing or invalid.",
    403: "Forbidden. Credentials are valid, but access is not allowed.",
    404: "Resource not found.",
    429: "Too many requests. The rate limit was exceeded.",
    500: "Internal server error. The server failed.",
    502: "Bad gateway.",
    503: "Service unavailable.",
}


def describe_status(status_code):
    """Task 20: use the status-code CATEGORY, not one generic message."""
    if 200 <= status_code < 300:
        return "Success."
    if status_code in STATUS_MESSAGES:
        return STATUS_MESSAGES[status_code]
    if 400 <= status_code < 500:
        return "Client error: the request was wrong."
    if status_code >= 500:
        return "Server error: the server failed."
    return "Unexpected status code."


def call_api(url, method="GET", timeout=TIMEOUT, **kwargs):
    """Send a request and ALWAYS return a result dictionary (never raise)."""
    try:
        response = requests.request(method, url, timeout=timeout, **kwargs)
    except requests.Timeout:
        return {
            "kind": "timeout",
            "status": None,
            "message": f"No response within {timeout} seconds.",
        }
    except requests.ConnectionError:
        return {
            "kind": "network_error",
            "status": None,
            "message": "Could not connect (network down, or the host does not exist).",
        }
    except requests.RequestException as error:
        return {"kind": "network_error", "status": None, "message": f"Request failed: {error}"}

    kind = "success" if 200 <= response.status_code < 300 else "api_error"
    return {
        "kind": kind,
        "status": response.status_code,
        "message": describe_status(response.status_code),
        "retry_after": response.headers.get("Retry-After"),
        "response": response,
    }


def report(result):
    """Print a result in the format the lab expects."""
    kind = result["kind"]
    if kind == "success":
        print("Request successful.")
        print(f"Status Code: {result['status']}")
    elif kind == "api_error":
        print("Request failed.")
        print(f"Status Code: {result['status']}")
        print(result["message"])
    elif kind == "timeout":
        print("Request failed.")
        print(f"Timeout: {result['message']}")
    else:
        print("Request failed.")
        print(f"Network error: {result['message']}")


def get_with_retry(url, max_attempts=3, base_delay=1):
    """Rate-limit friendly GET: on 429, wait (exponential backoff) and try again."""
    result = None
    for attempt in range(1, max_attempts + 1):
        result = call_api(url)
        if result["status"] != 429 or attempt == max_attempts:
            return result

        retry_after = result.get("retry_after")
        wait = int(retry_after) if retry_after and retry_after.isdigit() else base_delay * 2 ** (attempt - 1)
        print(f"  429 received (attempt {attempt}/{max_attempts}). Waiting {wait}s before retrying...")
        time.sleep(wait)
    return result


def main():
    print("=== Task 19: handle a 404 ===")
    report(call_api("https://jsonplaceholder.typicode.com/posts/9999"))

    print("\n=== Task 20: different HTTP status codes ===")
    for code in (200, 400, 401, 404, 429, 500):
        print(f"\n-> httpbin.org/status/{code}")
        report(call_api(f"https://httpbin.org/status/{code}"))

    print("\n=== Task 21: timeout (the server waits 5s, we only wait 2s) ===")
    report(call_api("https://httpbin.org/delay/5", timeout=2))

    print("\n=== Task 22: network failure (this host does not exist) ===")
    report(call_api("https://this-host-does-not-exist.invalid/"))

    print("\n=== Rate limits: retry with backoff on 429 ===")
    result = get_with_retry("https://httpbin.org/status/429")
    report(result)


if __name__ == "__main__":
    main()
