from pathlib import Path

from track_bump.config import Config, replace_in_files
from track_bump.tags import get_branch_release, get_latest_release_tag, get_latest_stable_tag, get_new_tag
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


def bump_project(
    config: Config,
    sign_commits: bool = False,
    branch: str | None = None,
    last_commit_message: str | None = None,
    dry_run: bool = False,
    force: bool = False,
    no_reset_git: bool = False,
    add_tag: bool = True,
    pre_release: str | None = None,
):
    """
    Bump the version of the project, create a commit and tag and commit the changes.
    You can also add files to be added to the commit.
    If add_tag is specified, it will also create a tag with the new version. Otherwise
    it'll just print the new tag.
    """
    # Setup git
    current_version = config.version
    with set_cd(config.project_path):
        with git_setup(sign_commits=sign_commits, no_reset=no_reset_git):
            # Get the latest stable and release tags for the branch
            fetch_tags(force=force)
            _latest_stable_tag = get_latest_stable_tag()
            _branch = branch or get_current_branch()
            _release = pre_release or get_branch_release(_branch, releases=config.releases)
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

            version_files = config.version_files + [f"{config.config_path.name}:version"]
            if not dry_run:
                replace_in_files(config.config_path, version_files, new_version)
            else:
                logger.info(
                    f"{DRY_RUN_START}Would replace version with {new_version} in files:\n - {'\n - '.join(version_files)}"
                )
            _bump_message = config.bump_message.format(current_version=current_version, new_version=new_version)
            if not dry_run:
                logger.info(f"Committing with message: {COMMIT_START}{_bump_message}{COMMIT_END}")
                git_commit(_bump_message)
                if add_tag:
                    git_tag(_new_tag)
            else:
                logger.info(
                    f"{DRY_RUN_START}Would commit with message: {COMMIT_START}{_bump_message}{COMMIT_END} "
                    f"and tag: {TAG_START}{_new_tag}{TAG_END}{DRY_RUN_END}"
                )
            logger.info("Done")
            if not add_tag:
                print(_new_tag)
