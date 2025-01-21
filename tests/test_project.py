import json
import shutil
import tomllib
from pathlib import Path

import pytest

from .conftest import DEFAULT_BRANCH, STATIC_DIR


def get_tags(project_path: Path):
    from track_bump.utils import get_tags, set_cd

    with set_cd(project_path):
        tags = get_tags()
    return tags


def get_toml_versions(project_path: Path):
    default_version = tomllib.loads((project_path / ".cz.toml").read_text())["tool"]["track-bump"]["version"]
    _sub_1 = tomllib.loads((project_path / "sub-project-1" / "pyproject.toml").read_text())["tool"]["poetry"]["version"]
    _sub_2 = tomllib.loads((project_path / "sub-project-2" / "pyproject.toml").read_text())["tool"]["poetry"]["version"]
    return {"default": default_version, "sub_1": _sub_1, "sub_2": _sub_2}


def get_js_versions(project_path: Path):
    default_version = json.loads((project_path / "package.json").read_text())["version"]
    return {"default": default_version}


class TestTOML:
    @pytest.fixture(scope="function")
    def project_path(self, tmp_path: Path):
        return tmp_path / "project"

    @pytest.fixture(scope="function")
    def setup_project(self, project_path: Path):
        shutil.copytree(STATIC_DIR / "project", project_path)
        from track_bump.utils import exec_cmd, git_setup, set_cd

        with set_cd(project_path):
            exec_cmd("git init")
            with git_setup(sign_commits=False, default_branch=DEFAULT_BRANCH):
                yield

    def test_bump(self, setup_project, project_path, monkeypatch):
        monkeypatch.setattr("track_bump.utils.get_last_commit_message", lambda: None)
        from track_bump.bump import bump_project
        from track_bump.config import Config

        config = Config.from_project(project_path)

        assert get_toml_versions(project_path) == {
            "default": "0.1.0",
            "sub_1": "0.1.0",
            "sub_2": "0.1.0",
        }, "Initial versions should be 0.1.0"
        assert get_tags(project_path) == [], "No tags should be present"

        bump_project(config=config, branch="develop")
        tags = ["v0.2.0-beta.0"]
        assert set(get_tags(project_path)) == set(tags)
        assert get_toml_versions(project_path) == {
            "default": "0.2.0-beta.0",
            "sub_1": "0.2.0-beta.0",
            "sub_2": "0.2.0-beta.0",
        }
        # Running it again
        tags.append("v0.2.0-beta.1")
        bump_project(config=config, branch="develop")
        assert set(get_tags(project_path)) == set(tags), "Tags should be incremented"
        assert get_toml_versions(project_path) == {
            "default": "0.2.0-beta.1",
            "sub_1": "0.2.0-beta.1",
            "sub_2": "0.2.0-beta.1",
        }

        # Changing to main, making a fix

        bump_project(config=config, last_commit_message="fix: a fix", branch=DEFAULT_BRANCH)
        tags.append("v0.1.1")
        assert set(get_tags(project_path)) == set(tags)
        assert get_toml_versions(project_path) == {"default": "0.1.1", "sub_1": "0.1.1", "sub_2": "0.1.1"}

        # Creating a release

        bump_project(config=config, branch=DEFAULT_BRANCH)
        tags.append("v0.2.0")
        assert set(get_tags(project_path)) == set(tags)
        assert get_toml_versions(project_path) == {"default": "0.2.0", "sub_1": "0.2.0", "sub_2": "0.2.0"}


class TestJSON:
    @pytest.fixture(scope="function")
    def project_path(self, tmp_path: Path):
        return tmp_path / "project-js"

    @pytest.fixture(scope="function")
    def setup_project(self, project_path: Path):
        shutil.copytree(STATIC_DIR / "project-js", project_path)
        from track_bump.utils import exec_cmd, git_setup, set_cd

        with set_cd(project_path):
            exec_cmd("git init")
            with git_setup(sign_commits=False, default_branch=DEFAULT_BRANCH):
                yield

    def test_bump(self, setup_project, project_path, monkeypatch):
        monkeypatch.setattr("track_bump.utils.get_last_commit_message", lambda: None)
        from track_bump.bump import bump_project
        from track_bump.config import Config

        config = Config.from_project(project_path)

        assert get_js_versions(project_path) == {
            "default": "0.1.0",
        }, "Initial versions should be 0.1.0"
        assert get_tags(project_path) == [], "No tags should be present"

        bump_project(config=config, branch="develop")
        tags = ["v0.2.0-beta.0"]
        assert set(get_tags(project_path)) == set(tags)
        assert get_js_versions(project_path) == {"default": "0.2.0-beta.0"}
        # Running it again
        tags.append("v0.2.0-beta.1")
        bump_project(config=config, branch="develop")
        assert set(get_tags(project_path)) == set(tags), "Tags should be incremented"
        assert get_js_versions(project_path) == {"default": "0.2.0-beta.1"}

        # Changing to main, making a fix

        bump_project(config=config, last_commit_message="fix: a fix")
        tags.append("v0.1.1")
        assert set(get_tags(project_path)) == set(tags)
        assert get_js_versions(project_path) == {"default": "0.1.1"}

        # Creating a release

        bump_project(config=config)
        tags.append("v0.2.0")
        assert set(get_tags(project_path)) == set(tags)
        assert get_js_versions(project_path) == {"default": "0.2.0"}
