import logging
from pathlib import Path

from piou import Cli, Option

from .bump import bump_project
from .env import DEFAULT_BRANCH
from .logs import init_logging as _init_logging
from .logs import logger
from .tags import get_branch_release_tag, get_latest_default_tag, get_latest_release_tag
from .utils import get_current_branch, set_cd

cli = Cli("Track-bump utility commands")

cli.add_option("-v", "--verbose", help="Verbosity")
cli.add_option("-vv", "--verbose2", help="Increased verbosity")
cli.add_option("--init-logging", help="Initialize logging")


def on_process(verbose: bool = False, verbose2: bool = False, init_logging: bool = False):
    logger.level = logging.DEBUG if verbose2 else logging.INFO if verbose else logging.WARNING
    logger.disabled = init_logging
    if init_logging:
        _init_logging(logger.level)


cli.set_options_processor(on_process)


@cli.command(cmd="bump", help="Bump project version")
def bump(
    project_path: Path = Option(Path.cwd(), "-p", "--project", help="Project path"),
    sign_commits: bool = Option(False, "--sign", help="Sign commits"),
    branch: str | None = Option(None, "--branch", help="Branch to bump"),
    dry_run: bool = Option(False, "--dry-run", help="Dry run"),
    force: bool = Option(False, "--force", help="Force fetch tags"),
):
    bump_project(project_path, sign_commits, branch=branch, dry_run=dry_run, force=force)


@cli.command(cmd="get-latest-tag", help="Get the latest tag")
def get_latest_tag(
    project_path: Path = Option(Path.cwd(), "-p", "--project", help="Project path"),
    branch: str | None = Option(None, "--branch", help="Branch to bump"),
):
    with set_cd(project_path):
        _branch = branch or get_current_branch()
        tag = (
            get_latest_default_tag()
            if _branch == DEFAULT_BRANCH
            else get_latest_release_tag(get_branch_release_tag(_branch))
        )
    if tag:
        print(tag)


def run():
    cli.run()


if __name__ == "__main__":
    run()
