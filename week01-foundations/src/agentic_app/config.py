"""Central application configuration, loaded from the .env file."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root = the folder that contains src/, tests/, data/ and .env
PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

APP_NAME = os.getenv("APP_NAME", "Student Information System")
DEBUG = os.getenv("DEBUG", "False")
MAX_STUDENTS = os.getenv("MAX_STUDENTS", "100")

# Sensitive value: loaded from the environment, never printed or hardcoded.
API_KEY = os.getenv("API_KEY")

DATA_FILE = PROJECT_ROOT / "data" / "student.json"
LOG_DIR = PROJECT_ROOT / "logs"
