import re
from typing import Literal

from .env import DEFAULT_BRANCH
from .logs import COMMIT_END, COMMIT_START, TAG_END, TAG_START, logger
from .utils import get_last_commit_message, get_last_tag, parse_version

__all__ = (
    "get_latest_default_tag",
    "get_latest_release_tag",
    "get_branch_release_tag",
    "get_new_tag",
    "ReleaseTag",
    "BranchName",
)

ReleaseTag = Literal["beta", "rc", "stable"]
type BranchName = str

_RELEASE_TAGS: dict[BranchName, ReleaseTag] = {
    r"^develop$": "beta",
    r"^release/.*": "rc",
    rf"^{DEFAULT_BRANCH}$": "stable",
}


def get_latest_default_tag():
    return get_last_tag(r"^v\d+\.\d+\.\d+$")


def get_latest_release_tag(release_tag: str) -> str | None:
    return get_last_tag(rf"^v\d+\.\d+\.\d+-{release_tag}\.\d+$")


def get_branch_release_tag(branch: BranchName) -> ReleaseTag:
    for branch_pattern, release_tag in _RELEASE_TAGS.items():
        if re.match(branch_pattern, branch):
            return release_tag
    raise ValueError(f"Branch {branch!r} is not supported")


_BUMP_MINOR_REG = re.compile(r"release:.*")


def get_new_tag(latest_tag: str | None, release_tag: ReleaseTag, last_commit_message: str | None = None) -> str:
    """
    Return the new tag based on the latest release tag and current branch
    """
    if not latest_tag:
        raise ValueError("No tags found. Please create a release tag first (like v0.1.0)")

    (major, minor, patch), _ = parse_version(latest_tag.removeprefix("v"))
    _next_release = f"v{major}.{minor + 1}.0"
    if release_tag != "stable":
        _latest_release_tag = get_latest_release_tag(release_tag)
        logger.info(f"Latest {release_tag} tag: {TAG_START}{_latest_release_tag}{TAG_END}")
        _release_number = int(_latest_release_tag.split(".")[-1]) + 1 if _latest_release_tag is not None else 0
        _tag = f"{_next_release}-{release_tag}.{_release_number}"
    else:
        _last_commit_message = last_commit_message or get_last_commit_message()
        logger.info(
            f"Last commit message: {COMMIT_START}{_last_commit_message}{COMMIT_END}"
            if _last_commit_message is not None
            else "No commit message found"
        )
        if _last_commit_message is None or _BUMP_MINOR_REG.match(_last_commit_message):
            logger.debug("Bumping minor")
            _tag = _next_release
        else:
            logger.debug("Bumping patch")
            _tag = f"v{major}.{minor}.{patch + 1}"

    return _tag
