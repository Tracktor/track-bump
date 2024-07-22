import logging

__all__ = ("logger", "init_logging")

logger = logging.getLogger("track-bump")


def init_logging(level: int = logging.WARNING):
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.setLevel(level)
