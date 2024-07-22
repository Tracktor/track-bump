from .utils import get_last_tag, parse_version
from .logs import logger
from .env import MAIN_BRANCH
from typing import Literal
import re

__all__ = (
    'get_latest_main_tag',
    'get_latest_release_tag',
    'get_branch_release_tag',
    'get_new_tag',
    'ReleaseTag',
    'BranchName'
)

type ReleaseTag = Literal["beta", "rc", "stable"]
type BranchName = str

_RELEASE_TAGS: dict[BranchName, ReleaseTag] = {
    r"^develop$": "beta",
    r"release/.*": "rc",
    rf"^{MAIN_BRANCH}": "stable"
}


def get_latest_main_tag():
    return get_last_tag(r"^v\d+\.\d+\.\d+$")


def get_latest_release_tag(release_tag: str) -> str | None:
    return get_last_tag(fr"^v\d+\.\d+\.\d+-{release_tag}\.\d+$")


def get_branch_release_tag(branch: BranchName) -> ReleaseTag:
    for branch_pattern, release_tag in _RELEASE_TAGS.items():
        if re.match(branch_pattern, branch):
            return release_tag
    raise ValueError(f"Branch {branch!r} is not supported")


def get_new_tag(latest_tag: str | None,
                release_tag: ReleaseTag) -> str:
    """
    Return the new tag based on the latest release tag and current branch
    """
    if not latest_tag:
        raise ValueError("No main tags found. Please create a release tag first (like v0.1.0)")
    logger.info(f"Latest tag: {latest_tag}")

    (major, minor, patch), _ = parse_version(latest_tag.removeprefix('v'))
    _next_release = f"v{major}.{minor + 1}.0"
    if release_tag != 'stable':
        print('getting latest release tag')
        _latest_release_tag = get_latest_release_tag(release_tag)
        logger.info(f"Latest {release_tag} tag: {_latest_release_tag}")
        _release_number = int(_latest_release_tag.split(".")[-1]) + 1 if _latest_release_tag is not None else 0
        _tag = f"{_next_release}-{release_tag}.{_release_number}"
    else:
        _tag = _next_release

    return _tag

