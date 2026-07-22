import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """Configure structured application logging for the API process."""

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        )
    )

    root_logger.addHandler(handler)
