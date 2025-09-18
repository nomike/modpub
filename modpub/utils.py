from __future__ import annotations
import logging
import os

def setup_logging() -> None:
    """Configure root logging once; level via MODPUB_LOG_LEVEL (default INFO)."""
    if getattr(setup_logging, "_configured", False):  # type: ignore[attr-defined]
        return
    level = os.getenv("MODPUB_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    setup_logging._configured = True  # type: ignore[attr-defined]
