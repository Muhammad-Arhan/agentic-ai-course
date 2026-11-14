# Week 2: Agent-Ready REST Service

A small REST API built with **FastAPI** that fetches its data from an external API
(JSONPlaceholder) through a clean, layered design:

```
Client (browser / Postman / curl / later: an AI agent)
   -> REST API (FastAPI)
      -> Route    routes/users.py          HTTP paths, methods, status codes, input validation
         -> Service  services/user_service.py   what to ask, convert raw JSON to our User model
            -> Client   clients/external_api.py    HTTP call, timeout, auth header, error handling
               -> External API   https://jsonplaceholder.typicode.com
```

## Setup (from this folder)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "import requests, httpx, fastapi; print('API stack OK')"
cp .env.example .env          # then edit the values if you want
```

## Run the service

```bash
uvicorn api_service.main:app --reload --app-dir src
```

Open http://127.0.0.1:8000/ (JSON message) and http://127.0.0.1:8000/docs (interactive Swagger UI).

## Run the tests

```bash
pytest
```

The tests never use the internet: the external API is replaced by a fake.

## API reference

| Operation | Method and endpoint | Request body | Success response |
| --- | --- | --- | --- |
| Welcome | `GET /` | - | `200` `{"message": "Agentic AI API is running"}` |
| Health check | `GET /health` | - | `200` `{"status", "service", "version"}` |
| List users | `GET /users` | - | `200` list of users |
| Get one user | `GET /users/{user_id}` | - | `200` one user |
| Create user | `POST /users` | `{"name", "username", "email"}` | `201` the created user |
| Update user | `PUT /users/{user_id}` | `{"name", "username", "email"}` | `200` the updated user |
| Delete user | `DELETE /users/{user_id}` | - | `204` (no body) |

**Parameters:** `user_id` is an integer, 1 or greater (otherwise `422`).

**Request body rules** (`POST` and `PUT`): `name` 1-100 characters, `username` 1-50 characters,
`email` must look like `a@b.c`. Example: `data/sample_user.json`.

**User response structure:**

```json
{"id": 1, "name": "Leanne Graham", "username": "Bret", "email": "Sincere@april.biz"}
```

### Possible errors

| Status | When | Notes |
| --- | --- | --- |
| `404` | The user does not exist (or an unknown URL) | `{"detail": "Resource not found."}` |
| `422` | Invalid input (missing field, bad email, `user_id` not a positive number) | FastAPI lists the invalid fields |
| `429` | The external API's rate limit was hit | Includes `Retry-After` when the external API sent it |
| `502` | The external API failed (500/502/503), could not be reached, rejected our credentials, or returned bad data | Our service is fine; the upstream is not |
| `504` | The external API did not answer within `REQUEST_TIMEOUT` seconds | |

Clients only ever see these clean responses, never stack traces or raw upstream failures.

### Try it with curl

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/users/1
curl -X POST http://127.0.0.1:8000/users -H "Content-Type: application/json" -d @data/sample_user.json
curl -i -X DELETE http://127.0.0.1:8000/users/1
```

## Configuration (`.env`)

| Variable | Default | Meaning |
| --- | --- | --- |
| `APP_NAME` | Agent-Ready REST Service | Name shown in `/health` and `/docs` |
| `EXTERNAL_API_BASE_URL` | https://jsonplaceholder.typicode.com | The external API |
| `REQUEST_TIMEOUT` | 10 | Seconds to wait for the external API |
| `LOG_LEVEL` | INFO | DEBUG, INFO, WARNING, ERROR |
| `API_KEY` | (empty) | If set, sent as `Authorization: Bearer <API_KEY>`. Never commit `.env`. |

## Project structure

```
src/api_service/   main.py, config.py, routes/, services/, clients/, models/
tests/             test_health.py, test_users.py, test_external_api.py, conftest.py
data/              sample request body
lab/               the instructor's Week 2 lab tasks (phases 01-06, evidence, study notes)
```

## How this becomes an agent tool

Every endpoint is a candidate tool for an AI agent. For example `GET /users/{user_id}`:

- **Tool name:** `get_user` - **Input:** `user_id` (integer) - **Output:** `id`, `name`, `username`, `email`
- **Errors the agent must understand:** `404` (no such user), `429` (wait, then retry), `502`/`504` (upstream problem, try later)
- The service already returns **predictable JSON and clear status codes**, validates inputs, applies a
  **timeout**, keeps credentials in `.env` and reports rate limits with `Retry-After`: exactly what an
  autonomous caller needs. The full specification is in `lab/phase06/tool_specification.md`.
