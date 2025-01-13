from pathlib import Path

from track_bump.tags import get_branch_release_tag, get_latest_default_tag, get_new_tag
from track_bump.update_files import parse_config_file, replace_in_files
from track_bump.utils import fetch_tags, get_current_branch, git_commit, git_setup, git_tag, parse_version, set_cd

from .logs import (
    BRANCH_END,
    BRANCH_START,
    COMMIT_END,
    COMMIT_START,
    DRY_RUN_END,
    DRY_RUN_START,
    RELEASE_TAG_END,
    RELEASE_TAG_START,
    TAG_END,
    TAG_START,
    logger,
)

CONFIG_FILES = [".cz.toml", "pyproject.toml"]


def bump_project(
    project_path: Path,
    sign_commits: bool = False,
    branch: str | None = None,
    last_commit_message: str | None = None,
    dry_run: bool = False,
    force: bool = False,
):
    logger.info(f"Bumping project in {project_path} (dry-run: {dry_run})")
    for file in CONFIG_FILES:
        config_path = Path(project_path / file)
        if config_path.exists():
            break
    else:
        raise FileNotFoundError(f"Could not find any of the following files: {CONFIG_FILES} in {project_path}")

    config = parse_config_file(config_path)

    git_setup(sign_commits=sign_commits)
    with set_cd(project_path):
        fetch_tags(force=force)
        _latest_tag = get_latest_default_tag()
        logger.info(f"Latest tag: {TAG_START}{_latest_tag}{TAG_END}")
        _branch = branch or get_current_branch()
        _release_tag = get_branch_release_tag(_branch)
        logger.info(
            f"Branch {BRANCH_START}{_branch}{BRANCH_END} (tag: {RELEASE_TAG_START}{_release_tag}{RELEASE_TAG_END})"
        )

        if _latest_tag is None:
            (major, minor, path), release = parse_version(config["version"])
            _latest_tag = f"v{major}.{max(minor - 1, 1)}.{path}"
        _new_tag = get_new_tag(
            latest_tag=_latest_tag, release_tag=_release_tag, last_commit_message=last_commit_message
        )

    current_version = config["version"]
    new_version = _new_tag.removeprefix("v")
    logger.info(f"New tag {TAG_START}{_new_tag}{TAG_END} (version: {new_version})")
    if dry_run:
        logger.info(
            f"{DRY_RUN_START}Would replace in files: {', '.join(config['version_files'])} "
            f"with version: {new_version}{DRY_RUN_END}"
        )
    else:
        replace_in_files(config_path, config["version_files"], new_version)
    _bump_message = config["bump_message"].format(current_version=current_version, new_version=new_version)
    if dry_run:
        logger.info(
            f"{DRY_RUN_START}Would commit with message: {COMMIT_START}{_bump_message}{COMMIT_END} "
            f"and tag: {TAG_START}{_new_tag}{TAG_END}{DRY_RUN_END}"
        )

    else:
        logger.info(f"Committing with message: {COMMIT_START}{_bump_message}{COMMIT_END}")
        with set_cd(project_path):
            git_commit(_bump_message)
            git_tag(_new_tag)
    logger.info("Done")
