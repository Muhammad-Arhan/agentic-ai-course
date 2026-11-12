"""Application logging setup (console + logs/application.log)."""

import logging

from agentic_app.config import LOG_DIR

LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "application.log"),
    ],
)

logger = logging.getLogger("agentic_app")
