"""Project configuration: folders, model names and optional .env settings."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root = the folder that contains src/, tests/, data/ and models/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

# Hugging Face downloads (tokenizers, embedding model) can be slow on a weak
# connection, so wait longer than the default 10 seconds. A value in .env wins.
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "60")

# --- folders ---------------------------------------------------------------
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

# --- files -----------------------------------------------------------------
SUPPORT_RAW_FILE = RAW_DATA_DIR / "support_messages.csv"
SUPPORT_CLEAN_FILE = PROCESSED_DATA_DIR / "support_messages_clean.csv"
DOCUMENTS_FILE = RAW_DATA_DIR / "documents.txt"
CLASSIFIER_FILE = MODELS_DIR / "support_classifier.joblib"

# --- pretrained models (downloaded once, then cached in ~/.cache/huggingface) -
TOKENIZER_MODELS = ["bert-base-uncased", "gpt2"]
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
