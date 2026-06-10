import logging
import os
import sys


def setup_logger():
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("ai_assistant")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    # File handler
    fh = logging.FileHandler("logs/app.log", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console handler (useful for Docker logs)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger
