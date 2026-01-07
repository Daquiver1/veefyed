"""Log configuration module - Heroku compatible."""

import logging
import os
import sys

IS_HEROKU = os.environ.get("DYNO") is not None


def setup_logger(name, log_file=None, level=logging.INFO):
    """Setup a logger with console output and optional file output.On Heroku, only uses console output (stdout)."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter(f"%(asctime)s [{name.upper()}] %(message)s")
    )
    logger.addHandler(console_handler)

    if not IS_HEROKU and log_file:
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setFormatter(
            logging.Formatter(f"%(asctime)s [{name.upper()}] %(message)s")
        )
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger


app_logger = setup_logger("app", "logs/app.log")
request_logger = setup_logger("request", "logs/request.log")
error_logger = setup_logger("error", "logs/error.log", level=logging.ERROR)
