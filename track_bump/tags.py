import re
from typing import Literal

from .env import DEFAULT_BRANCH
from .logs import COMMIT_END, COMMIT_START, TAG_END, TAG_START, logger
from .utils import get_last_commit_message, get_last_tag, parse_version

__all__ = (
    "get_latest_stable_tag",
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


def get_latest_stable_tag():
    f"""
    Get the latest tag of the DEFAULT_BRANCH branch (stable)
    For example:
     - if the DEFAULT_BRANCH has a tag v0.1.0, it will return v0.1.0
    """
    return get_last_tag(r"^v\d+\.\d+\.\d+$")


def get_latest_release_tag(release_tag: str) -> str | None:
    """
    Get the latest tag of the given release_tag
    For example:
        - if the release_tag is "beta", it will return the latest tag v0.1.0-beta.1
    """
    return get_last_tag(rf"^v\d+\.\d+\.\d+-{release_tag}\.\d+$")


def get_branch_release_tag(branch: BranchName) -> ReleaseTag:
    for branch_pattern, release_tag in _RELEASE_TAGS.items():
        if re.match(branch_pattern, branch):
            return release_tag
    raise ValueError(f"Branch {branch!r} is not supported")


_BUMP_MINOR_REG = re.compile(r"release:.*")


def get_new_tag(stable_tag: str | None, release_tag: ReleaseTag, last_commit_message: str | None = None) -> str:
    """
    Return the new tag based on the latest release tag and current branch

    """
    if not stable_tag:
        raise ValueError("No tags found. Please create a release tag first (like v0.1.0)")

    (major, minor, patch), _ = parse_version(stable_tag)
    _next_release = f"v{major}.{minor + 1}.0"
    logger.debug(f"Getting new tag with latest tag {stable_tag!r} and release tag {release_tag!r}")
    if release_tag != "stable":
        _latest_release_tag = get_latest_release_tag(release_tag)
        logger.info(f"Latest {release_tag} tag: {TAG_START}{_latest_release_tag}{TAG_END}")
        if _latest_release_tag is not None:
            (_latest_major, _latest_minor, _latest_patch), _ = parse_version(_latest_release_tag)
            print(f"{major}.{minor}", f"{_latest_major}.{_latest_minor}")
            if f"{major}.{minor}" == f"{_latest_major}.{_latest_minor}":
                _release_number = 0
            else:
                _release_number = _latest_patch + 1
        else:
            _release_number = 0
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
