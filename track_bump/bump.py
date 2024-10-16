from pathlib import Path
from .logs import (
    logger,
    TAG_START,
    TAG_END,
    BRANCH_START,
    BRANCH_END,
    COMMIT_START,
    COMMIT_END,
    DRY_RUN_START,
    DRY_RUN_END,
)

from track_bump.utils import set_cd, get_current_branch, git_setup, git_commit, git_tag, parse_version, fetch_tags
from track_bump.tags import get_latest_default_tag, get_branch_release_tag, get_new_tag
from track_bump.update_files import parse_config_file, replace_in_files

CONFIG_FILES = [".cz.toml", "pyproject.toml"]


def bump_project(
    project_path: Path,
    sign_commits: bool = False,
    branch: str | None = None,
    last_commit_message: str | None = None,
    dry_run: bool = False,
    force: bool = False,
):
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
        _tag = get_branch_release_tag(_branch)
        logger.info(f"Branch {BRANCH_START}{_branch}{BRANCH_END} (tag: [italic]{_tag}[/italic])")

        if _latest_tag is None:
            (major, minor, path), release = parse_version(config["version"])
            _latest_tag = f"v{major}.{max(minor - 1, 1)}.{path}"
        _new_tag = get_new_tag(latest_tag=_latest_tag, release_tag=_tag, last_commit_message=last_commit_message)

    current_version = config["version"]
    new_version = _new_tag.removeprefix("v")
    logger.info(f"New tag {TAG_START}{_new_tag}{TAG_END} (version: {new_version})")
    if dry_run:
        logger.info(
            f"{DRY_RUN_START}Would replace in files: {', '.join(config['version_files'])} with version: {new_version}{DRY_RUN_END}"
        )
    else:
        replace_in_files(config_path, config["version_files"], new_version)
    _bump_message = config["bump_message"].format(current_version=current_version, new_version=new_version)
    if dry_run:
        logger.info(
            f"{DRY_RUN_START}Would commit with message: {COMMIT_START}{_bump_message}{COMMIT_END} and tag: {TAG_START}{_new_tag}{TAG_END}{DRY_RUN_END}"
        )

    else:
        logger.info(f"Committing with message: {_bump_message}")
        with set_cd(project_path):
            git_commit(_bump_message)
            git_tag(_new_tag)
    logger.info("Done")
