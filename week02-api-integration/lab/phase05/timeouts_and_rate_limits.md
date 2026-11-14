# Phase 05 - Timeouts and rate limits

## Task 21 - Why is a timeout necessary?

```python
requests.get(url, timeout=10)
```

By default `requests` waits **forever**. If the server is overloaded, the network drops
packets or the connection hangs, the program would sit there for an unknown time and
everything that depends on it would freeze. A timeout sets a maximum wait. When it expires,
`requests.Timeout` is raised, we handle it (message, retry later, give up) and the program
carries on. In `api_client.py` a timeout is always set, and the timeout case is reported
separately from API errors and network failures.

## Task 23 - Rate limiting

**What is a rate limit?**
A rule that an API only accepts a certain number of requests from one client in a period of
time (for example, 60 requests per minute).

**Why do APIs impose rate limits?**
To protect the server from overload, to share capacity fairly between users, to stop abuse
and accidental floods, and to control costs. Paid APIs also use limits to separate pricing plans.

**What does HTTP 429 mean?**
"Too Many Requests": the client sent more requests than allowed. The request was not
processed. The response often has a `Retry-After` header saying how many seconds to wait.

**Why can an automated program generate too many requests?**
A program has no patience: a loop can send hundreds of requests per second. A bug (an
endless loop, a retry without delay) or a fast `for` over many items can exceed the
limit within seconds, which a human clicking in a browser never would.

**Why is this especially important for agentic systems?**
An AI agent decides by itself which tool to call and how often. Agents work in loops
(think, call a tool, observe, think again), may retry after failures, and several agents may run
in parallel, so their request volume is hard to predict. Without limits and backoff, an agent can
get blocked, run up a bill, or hammer a third-party service. Agent tools therefore need to
handle 429 (wait and retry with backoff, respect `Retry-After`) and cap the number of calls.

In this project: `ExternalApiClient` raises `RateLimitError` (with `retry_after`), our API
answers **429** with the same `Retry-After` header, and `phase05/api_client.py` shows an
exponential-backoff retry in `get_with_retry()`.
