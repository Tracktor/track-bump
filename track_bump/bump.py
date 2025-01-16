from pathlib import Path

from track_bump.tags import get_branch_release, get_latest_release_tag, get_latest_stable_tag, get_new_tag
from track_bump.update_files import parse_config_file, replace_in_files
from track_bump.utils import (
    fetch_tags,
    get_current_branch,
    get_last_commit_message,
    git_commit,
    git_setup,
    git_tag,
    parse_version,
    set_cd,
)

from .logs import (
    COMMIT_END,
    COMMIT_START,
    DRY_RUN_END,
    DRY_RUN_START,
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
    no_reset_git: bool = False,
):
    """
    Bump the version of the project, create a commit and tag and commit the changes.
    You can also add files to be added to the commit.
    """
    logger.info(f"Bumping project in {project_path} (dry-run: {dry_run})")
    # Check if any of the config files exist
    for file in CONFIG_FILES:
        config_path = Path(project_path / file)
        if config_path.exists():
            logger.debug(f"Found config file: {config_path}")
            break
    else:
        raise FileNotFoundError(f"Could not find any of the following files: {CONFIG_FILES} in {project_path}")

    config = parse_config_file(config_path)

    # Setup git
    current_version = config["version"]
    with set_cd(project_path):
        with git_setup(sign_commits=sign_commits, no_reset=no_reset_git):
            # Get the latest stable and release tags for the branch
            fetch_tags(force=force)
            _latest_stable_tag = get_latest_stable_tag()
            _branch = branch or get_current_branch()
            _release = get_branch_release(_branch)
            # If no latest tag, use the current version
            if _latest_stable_tag is None:
                (major, minor, path), release = parse_version(current_version)
                _latest_stable_tag = f"v{major}.{max(minor - 1, 1)}.{path}"

            _latest_release_tag = get_latest_release_tag(_release)
            _new_tag = get_new_tag(
                stable_tag=_latest_stable_tag,
                release_tag=_latest_release_tag,
                last_commit_message=last_commit_message or get_last_commit_message(),
                release=_release,
            )

            new_version = _new_tag.removeprefix("v")
            logger.info(
                f"Stable tag: {TAG_START}{_latest_stable_tag}{TAG_END} | "
                f"Latest release tag: {TAG_START}{_latest_release_tag}{TAG_END} | "
                f"New version: {new_version} "
                f"(branch: {_branch}, release: {_release})"
            )

            version_files = config["version_files"] + [f"{config_path.name}:version"]
            if dry_run:
                logger.info(
                    f"{DRY_RUN_START}Would replace version with {new_version} in files:\n - {'\n - '.join(version_files)}"
                )
            else:
                replace_in_files(config_path, version_files, new_version)
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
