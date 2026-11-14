# Week 2 lab guide

This folder holds the work for your instructor's **Week 2 lab** (Phases 01-06 + final integration).
The final integration project is the **Agent-Ready REST Service** in the folder above
(`../src/api_service`, `../tests`, `../README.md`, `../requirements.txt`).

Run every command **from the `week02-api-integration` folder**, with the virtual environment active:

```bash
source .venv/bin/activate
```

| Phase | Tasks | Where | How |
| --- | --- | --- | --- |
| 01 | 01-03 | `phase01/tasks.md` | Do the browser test, fill in the values, take 3 screenshots |
| 02 | 04-05, 10 | `phase02/tasks.md` | Written answers (already drafted, read and understand them) |
| 02 | 06-09 | `phase02/http_requests_demo.py` -> `phase02/results.md` | `python lab/phase02/http_requests_demo.py`, or use Postman (`postman_collection.json`) |
| 03 | 11-12 | `phase03/json_basics.py` | `python lab/phase03/json_basics.py` |
| 03 | 13-15 | `phase03/api_client.py` | `python lab/phase03/api_client.py` |
| 04 | 16 | `phase04/public_vs_protected.md` | Written comparison |
| 04 | 17-18 | `phase04/api_client.py`, `.env.example`, `.gitignore` | `cp .env.example .env`, set `API_KEY`, then `python lab/phase04/api_client.py` |
| 05 | 19-22 | `phase05/api_client.py` | `python lab/phase05/api_client.py` |
| 05 | 21, 23 | `phase05/timeouts_and_rate_limits.md` | Written answers |
| 06 | 24-25 | `phase06/tool_specification.md` | Tool specification (no agent yet) |
| Final | 26 | the project in the parent folder | See `../README.md` |
| - | - | `evidence/` | Your screenshots (list in `evidence/README.md`) |
| - | - | `STUDY_NOTES.md` | Revision notes for the viva |

## Using Postman for Tasks 06-09

1. Open Postman, then **File -> Import** and choose `lab/postman_collection.json`.
2. Folder **"Lab - JSONPlaceholder"** has the requests for Tasks 06-10 (GET x3, POST, PUT, DELETE, 404).
3. Click a request, press **Send**, and read the **Status** and the response body.
4. Screenshot each result for `evidence/`.
5. Folder **"Final project - local service"** calls your own FastAPI service (start it first).

## Notes

- These scripts call real websites: JSONPlaceholder (practice posts) and httpbin.org (practice
  errors, timeouts and Bearer authentication). You need an internet connection.
- JSONPlaceholder is a practice API: POST/PUT/DELETE look successful but never change its data.
- Your instructor's checklist is for **you** to tick: tick an item only after you have done and understood it.
