import shutil
import tomllib
from pathlib import Path

import pytest

from .conftest import DEFAULT_BRANCH, STATIC_DIR


@pytest.fixture(scope="function")
def project_path(tmp_path: Path):
    return tmp_path / "project"


@pytest.fixture(scope="function")
def setup_project(project_path: Path):
    shutil.copytree(STATIC_DIR / "project", project_path)
    from track_bump.utils import exec_cmd, git_setup, set_cd

    exec_cmd(f'git config --global init.defaultBranch "{DEFAULT_BRANCH}"')
    with set_cd(project_path):
        exec_cmd("git init")
        git_setup(sign_commits=False)


def get_tags(project_path: Path):
    from track_bump.utils import get_tags, set_cd

    with set_cd(project_path):
        tags = get_tags()
    return tags


def get_versions(project_path: Path):
    default_version = tomllib.loads((project_path / ".cz.toml").read_text())["tool"]["track-bump"]["version"]
    _sub_1 = tomllib.loads((project_path / "sub-project-1" / "pyproject.toml").read_text())["tool"]["poetry"]["version"]
    _sub_2 = tomllib.loads((project_path / "sub-project-2" / "pyproject.toml").read_text())["tool"]["poetry"]["version"]
    return {"default": default_version, "sub_1": _sub_1, "sub_2": _sub_2}


def test_bump(setup_project, project_path, monkeypatch):
    monkeypatch.setattr("track_bump.tags.get_last_commit_message", lambda: None)
    from track_bump.bump import bump_project

    assert get_versions(project_path) == {
        "default": "0.1.0",
        "sub_1": "0.1.0",
        "sub_2": "0.1.0",
    }, "Initial versions should be 0.1.0"
    assert get_tags(project_path) == [], "No tags should be present"

    bump_project(project_path, branch="develop")
    tags = ["v0.2.0-beta.0"]
    assert set(get_tags(project_path)) == set(tags)
    assert get_versions(project_path) == {"default": "0.2.0-beta.0", "sub_1": "0.2.0-beta.0", "sub_2": "0.2.0-beta.0"}
    # Running it again
    tags.append("v0.2.0-beta.1")
    bump_project(project_path, branch="develop")
    assert set(get_tags(project_path)) == set(tags), "Tags should be incremented"
    assert get_versions(project_path) == {"default": "0.2.0-beta.1", "sub_1": "0.2.0-beta.1", "sub_2": "0.2.0-beta.1"}

    # Changing to main, making a fix

    bump_project(project_path, last_commit_message="fix: a fix")
    tags.append("v0.1.1")
    assert set(get_tags(project_path)) == set(tags)
    assert get_versions(project_path) == {"default": "0.1.1", "sub_1": "0.1.1", "sub_2": "0.1.1"}

    # Creating a release

    bump_project(project_path)
    tags.append("v0.2.0")
    assert set(get_tags(project_path)) == set(tags)
    assert get_versions(project_path) == {"default": "0.2.0", "sub_1": "0.2.0", "sub_2": "0.2.0"}
