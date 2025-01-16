import contextlib
import os
import pathlib
import re
import subprocess

from track_bump.env import CI_USER, CI_USER_EMAIL

from .logs import logger

__all__ = (
    "exec_cmd",
    "get_last_tag",
    "git_tag",
    "git_setup",
    "set_cd",
    "get_current_branch",
    "git_commit",
    "parse_version",
    "get_tags",
    "get_last_commit_message",
    "fetch_tags",
    "get_default_branch",
)


def exec_cmd(
    cmd: str | list[str], *, env: dict | None = None, show_progress: bool = False, ignore_errors: bool = False
) -> str:
    default_shell = os.getenv("SHELL", "/bin/bash")
    logger.debug(f"Executing command {cmd!r}")
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable=default_shell, env=env, text=True
    )
    if show_progress:
        for line in process.stderr or []:
            logger.debug(f" {line.rstrip()}")

    stdout, stderr = process.communicate()
    exit_code = process.wait()
    if not ignore_errors and exit_code != 0:
        raise OSError(stderr)

    if stdout:
        logger.debug(f"Command output: {stdout!r}")
    return stdout


@contextlib.contextmanager
def set_cd(path: pathlib.Path):
    prev_cwd = pathlib.Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def fetch_tags(force: bool = False):
    logger.debug(f"Fetching tags (force: {force})")
    exec_cmd("git fetch --tags" + (" --force" if force else ""))


def get_tags():
    tags = exec_cmd("git tag --sort=-version:refname").split("\n")
    return [x.strip() for x in tags if x.strip()]


def get_last_tag(pattern: str) -> str | None:
    _tags = get_tags()
    _valid_tags = [_tag for _tag in _tags if re.match(pattern, _tag)]
    return _valid_tags[0] if _valid_tags else None


def git_tag(version: str):
    _output = exec_cmd(f"git tag {version}")
    if _output:
        logger.debug(f"tag output: {_output}")


@contextlib.contextmanager
def git_setup(sign_commits: bool = False, default_branch: str | None = None, no_reset: bool = False):
    _cached = {
        "user.email": get_git_email(ignore_errors=True),
        "user.name": get_git_user_name(ignore_errors=True),
        "init.defaultBranch": get_default_branch(ignore_errors=True),
    }

    _ci_user = CI_USER or get_git_user_name()
    if not _ci_user:
        raise ValueError("CI_USER must be set")

    _ci_email = CI_USER_EMAIL or get_git_email()
    if not _ci_email:
        raise ValueError("CI_USER_EMAIL must be set")

    exec_cmd(f'git config user.email "{CI_USER_EMAIL}"')
    exec_cmd(f'git config user.name "{CI_USER}"')
    if sign_commits:
        exec_cmd("git config commit.gpgSign true")
    if default_branch:
        exec_cmd(f'git config init.defaultBranch "{default_branch}"')
    yield
    if no_reset:
        return

    for key, value in _cached.items():
        if value:
            exec_cmd(f'git config {key} "{value}"')
        else:
            try:
                exec_cmd(f"git config --unset {key}")
            except OSError as e:
                logger.warning(f"Failed to run 'git config --unset {key}' ({e.args})")


def get_current_branch() -> str:
    return exec_cmd("git branch --show-current").strip()


def git_commit(message: str):
    exec_cmd("git add .")
    exec_cmd(f'git commit -m "{message}"')


def get_last_commit_message() -> str | None:
    _latest_commit = exec_cmd("git log -1 --pretty=%B").strip()
    return _latest_commit if _latest_commit else None


type MajorMinorPatch = tuple[int, int, int]
type ReleaseVersion = tuple[str, int]


def parse_version(version: str) -> tuple[MajorMinorPatch, ReleaseVersion | None]:
    """
    Parse the version string and return a tuple with the major, minor, patch and the release version if any
    For example:
    - v0.1.0-beta.1 -> ((0, 1, 0), ('beta', 1))
    - v0.1.0 -> ((0, 1, 0), None)
    """

    _version, *_release = version.removeprefix("v").split("-")
    major, minor, patch = [int(x) for x in _version.split(".")]

    if _release:
        _release_name, _release_number_str = _release[0].split(".")
        release = (_release_name, int(_release_number_str))
    else:
        release = None
    return (major, minor, patch), release


def get_git_email(ignore_errors: bool = False):
    return exec_cmd("git config user.email", ignore_errors=ignore_errors).strip()


def get_git_user_name(ignore_errors: bool = False):
    return exec_cmd("git config user.name", ignore_errors=ignore_errors).strip()


def get_gpg_sign(ignore_errors: bool = False):
    return exec_cmd("git config commit.gpgSign", ignore_errors=ignore_errors).strip()


def get_default_branch(ignore_errors: bool = False):
    return exec_cmd("git config init.defaultBranch", ignore_errors=ignore_errors).strip()
