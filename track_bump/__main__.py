import logging
from pathlib import Path

from piou import Cli, Option
from .logs import init_logging
from .bump import bump_project

cli = Cli("Track-bump utility commands")

cli.add_option("-v", "--verbose", help="Verbosity")
cli.add_option("-vv", "--verbose2", help="Increased verbosity")


def on_process(verbose: bool = False, verbose2: bool = False):
    init_logging(logging.DEBUG if verbose2 else logging.INFO if verbose else logging.WARNING)


cli.set_options_processor(on_process)


@cli.command(cmd="bump", help="Bump project version")
def bump(
        project_path: Path = Option(..., '-p', '--project', help="Project path"),
        sign_commits: bool = Option(False, '--sign', help="Sign commits"),
):
    bump_project(project_path, sign_commits)


def run():
    cli.run()


if __name__ == "__main__":
    run()
