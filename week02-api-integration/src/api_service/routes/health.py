"""Health check route: lets people (and later, orchestrators) see the API is alive."""

from fastapi import APIRouter

from api_service.config import APP_NAME, APP_VERSION

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok", "service": APP_NAME, "version": APP_VERSION}
