# Phase 02 - HTTP Requests, Responses and REST

Tasks 06-09 are executed by `http_requests_demo.py` (or by Postman, see `../README.md`).
The script writes the exact recorded results to **`results.md`**.

## Task 04 - Analyze a URL: `https://api.example.com/students/101`

| Part | Value |
| --- | --- |
| Protocol | `https` |
| Host | `api.example.com` |
| Path | `/students/101` |
| Resource | `students` |
| Resource identifier | `101` |

## Task 05 - REST API operation table

| Operation | HTTP method | Endpoint |
| --- | --- | --- |
| Retrieve all students | GET | /students |
| Create a student | POST | /students |
| Retrieve student 101 | GET | /students/101 |
| Update student 101 | PUT | /students/101 |
| Delete student 101 | DELETE | /students/101 |

**Why different HTTP methods?**
The URL says *which* resource (`/students/101`); the method says *what to do* with it. The same
URL is used for three different actions (read, update, delete), so the method is the only way
the server can tell them apart. Standard methods also make an API predictable: any developer
(or AI agent) who knows that GET reads and DELETE removes can use a new API without guessing.
GET never changes data, so it is safe to repeat; POST, PUT and DELETE change data, so clients
treat them more carefully.

## Tasks 06-09 - Recorded in `results.md`

| Task | Request | Expected status |
| --- | --- | --- |
| 06 | GET /posts/1, /posts/2, /posts/3 | 200 OK |
| 07 | POST /posts with the body `{"title": "My API Lab", "body": "Testing POST request", "userId": 1}` | 201 Created |
| 08 | PUT /posts/1 with an updated body | 200 OK |
| 09 | DELETE /posts/1 | 200 OK (empty `{}` body) |

**Task 09 - what is DELETE intended to accomplish?**
DELETE asks the server to remove the resource identified by the URL, here post 1. JSONPlaceholder
is a practice API: it accepts POST, PUT and DELETE and answers as if they worked, but it does **not**
really change its data, so `GET /posts/1` still works afterwards. A real API would return 404 for
that post after a successful delete.

## Task 10 - HTTP status codes

| Status code | Meaning | My test |
| --- | --- | --- |
| 200 | OK: the request succeeded and the response contains the result | `GET /posts/1` |
| 201 | Created: a new resource was created | `POST /posts` |
| 404 | Not Found: the server works, but that resource does not exist | `GET /posts/9999` |

**Successful request vs resource-not-found**
A 2xx status (200, 201) means the server understood the request *and did what was asked*. A 404 also
means the server answered correctly, but the **resource** named in the URL does not exist, so the
operation could not be done. In both cases the server is working; in the 404 case the client asked
for something that is not there (a 4xx client-side error), so the client should handle it
instead of treating the response body as data.
