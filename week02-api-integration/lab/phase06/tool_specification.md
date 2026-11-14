# Phase 06 - From API integration to agent tools

> No AI agent is built here. The goal is to see how an API operation becomes a **tool** an agent
> could call later.

## Task 24 - Tool specification

Selected operation: **retrieve one post** (implemented in `phase03/api_client.py` and `phase05/api_client.py`).

| Field | Value |
| --- | --- |
| Tool Name | `get_post` |
| Description | Retrieve one blog post by its numeric ID. |
| HTTP Method | `GET` |
| Endpoint | `https://jsonplaceholder.typicode.com/posts/{post_id}` |
| Required Inputs | `post_id` (integer, 1 or greater) |
| Optional Inputs | none |
| Expected Output | JSON object: `userId`, `id`, `title`, `body` |
| Possible Errors | `404` post does not exist, `429` rate limit exceeded, `500` server error, timeout (no answer in 10 s), network failure |
| Authentication Required | No (public API). A protected API would need `Authorization: Bearer <API_KEY>`, with the key read from `.env`. |

## Task 25 - Agent-oriented tool interface

```
Tool: get_post

Purpose:
    Retrieve a post using its ID.

Input:
    post_id (integer)

Output:
    id, title, body, userId

Possible Errors:
    404      -> "Post not found. Check the post_id."
    429      -> "Rate limit reached. Wait before calling again."
    500      -> "The posts service failed. Try again later."
    Timeout  -> "The posts service did not answer in time."
```

The same definition as a machine-readable schema (the format agent frameworks use to describe a tool):

```json
{
  "name": "get_post",
  "description": "Retrieve one blog post by its numeric ID. Returns id, title, body and userId.",
  "input_schema": {
    "type": "object",
    "properties": {
      "post_id": {"type": "integer", "minimum": 1, "description": "ID of the post to retrieve"}
    },
    "required": ["post_id"]
  }
}
```

## Why authentication and error handling still matter for a tool

- A tool call is made by software, not a person, so there is nobody to notice a strange response.
  The tool must return a **clear, structured error** the agent can reason about ("not found",
  "rate limited, retry later") and never an unhandled exception.
- A tool must not leak or hardcode credentials; the key stays in `.env` / environment variables.
- Timeouts and rate-limit handling stop an agent loop from hanging or flooding the API.

## Second example: the service's own endpoint (the final project)

| Field | Value |
| --- | --- |
| Tool Name | `get_user` |
| Description | Retrieve one user by ID from the Agent-Ready REST Service. |
| HTTP Method / Endpoint | `GET http://127.0.0.1:8000/users/{user_id}` |
| Required Inputs | `user_id` (integer, 1 or greater) |
| Expected Output | `{"id", "name", "username", "email"}` |
| Possible Errors | `404` unknown user, `422` invalid id, `429` rate limited (`Retry-After` header), `502` upstream failed, `504` upstream timed out |
| Authentication Required | No (local practice service) |
