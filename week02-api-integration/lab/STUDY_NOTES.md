# Week 2 study notes (read before your viva)

## Phase 01 - APIs
- **API** = Application Programming Interface: a defined way for one program to ask another for data or actions.
- Flow: **Client -> API -> Server -> Client**. The client does not need to know how the server works inside.
- Clients: browser, mobile app, Python program (our client in this course), AI agent (later).
- Request: `GET /students/101`. Response: JSON with the student's data.

## Phase 02 - HTTP and REST
- **HTTP** is the request/response protocol of the web.
- URL `https://api.example.com/students/101`: protocol `https`, host `api.example.com`, path `/students/101`.
- **Endpoint** = a specific API location for a resource (`/students`, `/students/101`).
- Methods: GET retrieve, POST create, PUT update/replace, DELETE remove.
- Status codes: **2xx** success (200 OK, 201 Created, 204 No Content) | **4xx** client error (400 Bad Request,
  401 Unauthorized, 403 Forbidden, 404 Not Found, 429 Too Many Requests) | **5xx** server error (500, 502, 503).
- Headers = metadata: `Accept`, `Content-Type`, `Authorization: Bearer TOKEN`.
- **REST**: APIs organized around resources. **HTTP method + resource = operation.**

## Phase 03 - JSON and Python
- JSON object `{...}` = Python **dict**. JSON array `[...]` = Python **list** (of dicts).
- `response.json()` converts JSON text to Python objects. `json.dumps()` goes back.

## Phase 04 - Authentication
- Public API: no credentials. Protected API: credentials in every request.
- API key / Bearer token / Basic auth / OAuth. For us: `Authorization: Bearer <key>`.
- Never hardcode keys: keep them in `.env`, read with `os.getenv`, and put `.env` in `.gitignore`.

## Phase 05 - Failure
- A request can fail because of: bad request, unauthorized, missing resource, rate limit, server failure, network failure, timeout.
- **Response received != operation succeeded**: always check the status code.
- Always set `timeout=`. Handle `requests.Timeout` and `requests.ConnectionError` separately.
- Rate limit: too many requests -> **429**; wait (`Retry-After`) and retry with backoff. Critical for agents (autonomous loops).

## Phase 06 - APIs as tools
- An API operation can become an agent tool: name, description, inputs, output, errors, authentication.
- Auth, timeouts and error handling matter MORE for tools, because software (not a person) is calling.

## This project in one picture
```
Client (browser / Postman / curl)
   -> FastAPI app  (main.py: error translation)
      -> Route     (routes/users.py: paths, methods, status codes, validation)
         -> Service (services/user_service.py: what to ask, convert to User)
            -> Client (clients/external_api.py: HTTP, timeout, auth, exceptions)
               -> External API (JSONPlaceholder)
```
