import os
from pathlib import Path
import logging
import pytest

MAIN_BRANCH = 'master'
os.environ['MAIN_BRANCH'] = MAIN_BRANCH
os.environ['CI_USER'] = 'foo'
os.environ['CI_USER_EMAIL'] = 'foo@bar.com'

STATIC_DIR = Path(__file__).parent / 'static'


@pytest.fixture(scope='session', autouse=True)
def setup_logging():
    from track_bump.logs import init_logging
    init_logging(logging.INFO)
