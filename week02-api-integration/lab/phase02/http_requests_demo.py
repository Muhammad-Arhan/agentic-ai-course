"""Phase 02 - Tasks 06-10: GET, POST, PUT, DELETE and status codes.

Sends real requests to JSONPlaceholder and records, for each one:
endpoint, HTTP method, request body, status code and response body.
The record is printed AND saved to results.md (your evidence for Tasks 06-10).

Run from the week02-api-integration folder:
    python lab/phase02/http_requests_demo.py
"""

import json
from pathlib import Path

import requests

BASE_URL = "https://jsonplaceholder.typicode.com"
TIMEOUT = 10
RESULTS_FILE = Path(__file__).parent / "results.md"

records = []


def send(task, method, endpoint, body=None):
    """Send one request and record everything we need for the lab report."""
    url = BASE_URL + endpoint
    print(f"\n[{task}] {method} {endpoint}")
    try:
        response = requests.request(method, url, json=body, timeout=TIMEOUT)
    except requests.RequestException as error:
        print(f"  Request failed: {error}")
        records.append((task, method, endpoint, body, "no response", str(error)))
        return None

    try:
        response_body = json.dumps(response.json(), indent=2)
    except ValueError:
        response_body = response.text

    print(f"  Status code: {response.status_code}")
    print(f"  Response body: {response_body[:300]}")
    records.append((task, method, endpoint, body, response.status_code, response_body))
    return response


def save_results():
    lines = ["# Phase 02 - recorded API requests (Tasks 06-10)", ""]
    for task, method, endpoint, body, status, response_body in records:
        lines += [
            f"## {task}",
            "",
            f"- HTTP method: `{method}`",
            f"- Endpoint: `{endpoint}`",
            f"- Status code: `{status}`",
            "",
        ]
        if body is not None:
            lines += ["Request body:", "```json", json.dumps(body, indent=2), "```", ""]
        lines += ["Response body:", "```json", response_body, "```", ""]
    RESULTS_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nSaved to {RESULTS_FILE}")


def main():
    # Task 06 - three GET requests
    for post_id in (1, 2, 3):
        send("Task 06 - GET", "GET", f"/posts/{post_id}")

    # Task 07 - POST creates a resource (JSONPlaceholder pretends: it returns id 101)
    send(
        "Task 07 - POST", "POST", "/posts",
        {"title": "My API Lab", "body": "Testing POST request", "userId": 1},
    )

    # Task 08 - PUT replaces a resource
    send(
        "Task 08 - PUT", "PUT", "/posts/1",
        {"id": 1, "title": "Updated title", "body": "Updated by my API lab", "userId": 1},
    )

    # Task 09 - DELETE removes a resource
    send("Task 09 - DELETE", "DELETE", "/posts/1")

    # Task 10 - observe 200, 201 and 404 (all three are already above, plus a 404)
    send("Task 10 - 404 test", "GET", "/posts/9999")

    save_results()


if __name__ == "__main__":
    main()
