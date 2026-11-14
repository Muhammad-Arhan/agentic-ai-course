# Task 16 - Public API vs protected API

| | Public API | Protected API |
| --- | --- | --- |
| Credentials required? | No. Anyone can send requests. | Yes. Every request must prove who is calling. |
| Why authentication is used | Not needed for open, read-only data (e.g. JSONPlaceholder). | To identify the caller, limit access to allowed users, protect private data, and track or limit usage (and bill for it). |
| Example mechanism | None (maybe a rate limit per IP address). | API key, Bearer token (`Authorization: Bearer TOKEN`), Basic authentication, OAuth. |
| Invalid credentials | Not applicable. | The server answers **401 Unauthorized** (missing/invalid credentials) or **403 Forbidden** (valid credentials, no permission). The data is not returned. |

## Where the credential goes

```
Python application --(Authorization: Bearer TOKEN)--> Protected API
```

## Keep the key out of the source code

```python
# BAD  - ends up on GitHub for everybody to see
API_KEY = "secret-key"

# GOOD - the value lives in .env (which is in .gitignore)
import os
api_key = os.getenv("API_KEY")
```

## Task 18 checklist (run these in `week02-api-integration/`)

```bash
cp .env.example .env              # create .env, then set API_KEY=your-practice-token
git check-ignore -v .env          # prints the .gitignore rule that excludes it
git status --short                # .env must NOT be listed
git ls-files | grep -x '.env' || echo ".env is not tracked"
```
