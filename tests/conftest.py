import logging
import os
from pathlib import Path

import pytest

STATIC_DIR = Path(__file__).parent / "static"
DEFAULT_BRANCH = "master"


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    from track_bump.logs import init_logging, logger

    init_logging(logging.WARNING)
    logger.console.quiet = True


@pytest.fixture(scope="session", autouse=True)
def setup_env():
    os.environ.update(
        DEFAULT_BRANCH=DEFAULT_BRANCH,
        CI_USER="foo",
        CI_USER_EMAIL="foo@bar.com",
    )
