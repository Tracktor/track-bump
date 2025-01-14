import re
from typing import Literal

from .env import DEFAULT_BRANCH
from .logs import COMMIT_END, COMMIT_START, TAG_END, TAG_START, logger
from .utils import get_last_tag, parse_version

__all__ = (
    "get_latest_stable_tag",
    "get_latest_release_tag",
    "get_branch_release",
    "get_new_tag",
    "Release",
    "BranchName",
)

Release = Literal["beta", "rc", "stable"]
type BranchName = str

_RELEASES: dict[BranchName, Release] = {
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


def get_branch_release(branch: BranchName) -> Release:
    """
    Get the release name for the given branch
    """

    for branch_pattern, release_tag in _RELEASES.items():
        if re.match(branch_pattern, branch):
            return release_tag
    raise ValueError(f"Branch {branch!r} is not supported")


_BUMP_MINOR_REG = re.compile(r"release:.*")


def get_new_tag(
    stable_tag: str,
    release_tag: str | None,
    release: str,
    last_commit_message: str | None = None,
) -> str:
    """
    Return the new tag based on the latest release tag and current branch
    Rules are:
     - if branch is not stable:
        - if the latest stable tag is v0.1.0 and the latest release tag is v0.2.0-beta.1:  v0.2.0-beta.2
        - if the latest stable tag is v0.1.0 and there is no latest release tag: v0.2.0-beta.0
    - if branch is stable and the latest stable tag is v0.1.0:
        - if the last commit message is "release: .*": v0.2.0
        - else: v0.1.1
    """
    (major, minor, patch), _ = parse_version(stable_tag)
    _next_release = f"v{major}.{minor + 1}.0"
    # We are releasing a new version
    if release == "stable":
        logger.info(
            f"Last commit message: {COMMIT_START}{last_commit_message}{COMMIT_END}"
            if last_commit_message is not None
            else "No commit message found"
        )
        if last_commit_message is None or _BUMP_MINOR_REG.match(last_commit_message):
            logger.debug("Bumping minor")
            _tag = _next_release
        else:
            logger.debug("Bumping patch")
            _tag = f"v{major}.{minor}.{patch + 1}"
    else:
        if release_tag is not None:
            (_release_major, _release_minor, _release_patch), _tag_part = parse_version(release_tag)
            if _tag_part is None:
                raise ValueError(f"Invalid tag: {release_tag!r}")
            (_tag, _tag_version) = _tag_part
            if f"{major}.{minor}.{patch}" == f"{_release_major}.{_release_minor}.{_release_patch}":
                _release_number = 0
            else:
                _release_number = _tag_version + 1
        else:
            _release_number = 0
        _tag = f"{_next_release}-{release}.{_release_number}"

    return _tag
