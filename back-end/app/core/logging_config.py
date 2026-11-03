import logging


def configure_logging(level: str) -> None:
    """Configure the root logger with a single console handler."""
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )
