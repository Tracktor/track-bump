import os
from pathlib import Path
import logging
import pytest

DEFAULT_BRANCH = "master"
os.environ["DEFAULT_BRANCH"] = DEFAULT_BRANCH
os.environ["CI_USER"] = "foo"
os.environ["CI_USER_EMAIL"] = "foo@bar.com"

STATIC_DIR = Path(__file__).parent / "static"


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    from track_bump.logs import init_logging, console

    init_logging(logging.WARNING)
    console.quiet = True
