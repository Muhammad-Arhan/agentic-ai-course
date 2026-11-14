"""Phase 04 - Tasks 17-18: Authorization header + credentials from .env.

Uses httpbin.org/bearer, a practice API that behaves like a protected API:
  * request WITH "Authorization: Bearer <token>"  -> 200 OK
  * request WITHOUT credentials                   -> 401 Unauthorized
(httpbin accepts any non-empty token, so a made-up practice token is fine.
Never put a real, valuable key in a practice script.)

Setup (from the week02-api-integration folder):
    cp .env.example .env        # then set API_KEY=any-practice-token
Run:
    python lab/phase04/api_client.py
"""

import os
import sys

import requests
from dotenv import load_dotenv

# Reads API_KEY from a .env file next to this script, or in a parent folder.
load_dotenv()

API_KEY = os.getenv("API_KEY")  # never written directly in the source code
URL = "https://httpbin.org/bearer"
TIMEOUT = 10


def build_headers(api_key):
    """Task 17: Authorization: Bearer TOKEN"""
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }


def sanitized(headers):
    """A copy of the headers that is safe to print or screenshot."""
    safe = dict(headers)
    if "Authorization" in safe:
        safe["Authorization"] = "Bearer ********"
    return safe


def main():
    if not API_KEY or API_KEY == "your_key_here":
        print("API_KEY is not set. Copy .env.example to .env and set API_KEY.")
        sys.exit(1)

    headers = build_headers(API_KEY)
    print("Request configuration (sanitized):")
    print(f"  GET {URL}")
    print(f"  headers: {sanitized(headers)}")

    print("\n--- With credentials ---")
    try:
        response = requests.get(URL, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as error:
        print(f"Request failed: {error}")
        sys.exit(1)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Authenticated: {response.json().get('authenticated')}")
    elif response.status_code == 401:
        print("Authentication failed: the credentials were rejected.")

    print("\n--- Without credentials (what a protected API does) ---")
    try:
        response = requests.get(URL, timeout=TIMEOUT)
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("Authentication failed: no credentials were sent.")
    except requests.RequestException as error:
        print(f"Request failed: {error}")


if __name__ == "__main__":
    main()
