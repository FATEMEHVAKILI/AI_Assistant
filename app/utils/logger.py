import logging
import os


def setup_logger():
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("ai_assistant")
    logger.setLevel(logging.INFO)

    # Avoid adding multiple handlers if reloaded
    if not logger.handlers:
        # File handler
        fh = logging.FileHandler("logs/app.log")
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # Console handler (useful for Docker logs)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger
