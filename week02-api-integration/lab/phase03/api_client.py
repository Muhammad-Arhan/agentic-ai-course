"""Phase 03 - Tasks 13-15: your first Python API client.

Talks to JSONPlaceholder with the `requests` library.

Run from the week02-api-integration folder:
    python lab/phase03/api_client.py
"""

import requests

BASE_URL = "https://jsonplaceholder.typicode.com"
TIMEOUT = 10  # seconds. Timeouts are explained properly in Phase 05.


def task_13_single_post():
    print("=== Task 13: one post ===")
    response = requests.get(f"{BASE_URL}/posts/1", timeout=TIMEOUT)

    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print("Request failed.")
        return

    post = response.json()  # JSON text -> Python dictionary
    print(f"Post ID: {post['id']}")
    print(f"Title: {post['title']}")
    print(f"Body: {post['body']}")


def task_14_multiple_posts():
    print("\n=== Task 14: posts 1, 2 and 3 (one loop, not three copies) ===")
    for post_id in (1, 2, 3):
        response = requests.get(f"{BASE_URL}/posts/{post_id}", timeout=TIMEOUT)
        if response.status_code == 200:
            print(f"Post {post_id}: {response.json()['title']}")
        else:
            print(f"Post {post_id}: request failed with status {response.status_code}")


def task_15_collection():
    print("\n=== Task 15: the whole collection ===")
    response = requests.get(f"{BASE_URL}/posts", timeout=TIMEOUT)

    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print("Request failed.")
        return

    posts = response.json()  # JSON array -> Python list of dictionaries
    print(f"Number of posts: {len(posts)}")
    print("First five titles:")
    for post in posts[:5]:
        print(f"  {post['id']}. {post['title']}")


if __name__ == "__main__":
    task_13_single_post()
    task_14_multiple_posts()
    task_15_collection()
