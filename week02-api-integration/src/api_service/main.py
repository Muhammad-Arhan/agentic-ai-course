"""FastAPI application entry point.

Run from the project root:
    uvicorn api_service.main:app --reload --app-dir src

Then open http://127.0.0.1:8000/docs
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api_service.clients.external_api import (
    ApiConnectionError,
    ApiTimeoutError,
    ExternalApiError,
    NotFoundError,
    RateLimitError,
)
from api_service.config import APP_NAME, APP_VERSION, LOG_LEVEL
from api_service.routes import health, users

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Client -> REST API -> Route -> Service -> External API",
)

app.include_router(health.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"message": "Agentic AI API is running"}


@app.exception_handler(ExternalApiError)
async def handle_external_api_error(request: Request, exc: ExternalApiError):
    """Translate failures of the external API into proper responses of OUR API.

    Our callers never see raw upstream failures or stack traces:
      404 upstream      -> 404 (resource really does not exist)
      429 upstream      -> 429 (+ Retry-After when the upstream sent one)
      timeout           -> 504 Gateway Timeout
      anything else     -> 502 Bad Gateway (the upstream misbehaved)
    """
    headers = None

    if isinstance(exc, NotFoundError):
        status_code, detail = 404, "Resource not found."
    elif isinstance(exc, RateLimitError):
        status_code, detail = 429, "Rate limit exceeded. Please try again later."
        if exc.retry_after is not None:
            headers = {"Retry-After": str(exc.retry_after)}
    elif isinstance(exc, ApiTimeoutError):
        status_code, detail = 504, "The external API timed out."
    elif isinstance(exc, ApiConnectionError):
        status_code, detail = 502, "Could not reach the external API."
    else:
        status_code, detail = 502, "The external API returned an error."

    logger.warning(
        "%s on %s %s -> returning %s", type(exc).__name__, request.method, request.url.path, status_code
    )
    return JSONResponse(status_code=status_code, content={"detail": detail}, headers=headers)
