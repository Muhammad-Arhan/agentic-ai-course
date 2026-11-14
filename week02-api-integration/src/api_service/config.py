"""Application configuration, loaded from environment variables / the .env file."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root = the folder that contains src/, tests/, data/ and .env
PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


def _float_env(name, default):
    """Read a float from the environment, falling back to a default."""
    try:
        return float(os.getenv(name, default))
    except ValueError:
        return float(default)


APP_NAME = os.getenv("APP_NAME", "Agent-Ready REST Service")
APP_VERSION = "0.2.0"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# The external API this service talks to (Route -> Service -> External API).
EXTERNAL_API_BASE_URL = os.getenv(
    "EXTERNAL_API_BASE_URL", "https://jsonplaceholder.typicode.com"
)

# Optional credential. Never hardcode it: it comes from .env / the environment.
EXTERNAL_API_KEY = os.getenv("API_KEY")

# Maximum seconds to wait for the external API (see Phase 05: timeouts).
REQUEST_TIMEOUT = _float_env("REQUEST_TIMEOUT", "10")
