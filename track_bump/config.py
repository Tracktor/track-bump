import json
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .logs import logger

__all__ = ("Config", "replace_in_file", "replace_in_files")

from track_bump import env


def get_default_releases() -> dict[str, str]:
    return {
        r"^develop$": "beta",
        r"^release/.*": "rc",
        rf"^{env.DEFAULT_BRANCH}$": "stable",
    }


def replace_in_file(file_path: Path, version: str, tag: str):
    """
    Replace the tag with the new version in the given file
    For example, if the file contains:
        version = "0.1.0"
    and you call replace_in_file(file_path, "0.2.0", "version")
    The file will be updated to:
        version = "0.2.0"
    """
    match file_path.suffix:
        case ".toml":
            _new_text = re.sub(rf'^{tag} = "(.*)"$', rf'{tag} = "{version}"', file_path.read_text(), flags=re.MULTILINE)
        case ".json":
            _new_text = re.sub(rf'"({tag})": "(.*)"', rf'"{tag}": "{version}"', file_path.read_text())
        case _:
            raise ValueError(f"Only .toml and .json files are supported")
    file_path.write_text(_new_text)


CONFIG_FILES = [".cz.toml", "pyproject.toml", "package.json"]


@dataclass
class Config:
    version: str
    bump_message: str
    version_files: list[str]
    default_branch: str
    releases: dict[str, str] = field(default_factory=get_default_releases)

    _config_path: Path = field(init=False)

    # def __post_init__(self):
    #     if self.default_branch not in self.releases:
    #         raise ValueError(f"Default branch {self.default_branch!r} is not supported in releases."
    #                          f" Supported branches are: {', '.join(self.releases.keys())}")

    @property
    def config_path(self) -> Path:
        return self._config_path

    @property
    def project_path(self) -> Path:
        return self._config_path.parent

    @classmethod
    def from_file(cls, config_path: Path, default_branch: str = env.DEFAULT_BRANCH):
        if not config_path.exists():
            raise FileNotFoundError(f"{config_path} not found")
        logger.debug(f"Parsing {config_path}")

        if config_path.suffix == ".toml":
            data = tomllib.loads(config_path.read_text())
            _config = data.get("tool", {}).get("track-bump")
            if _config is None:
                raise ValueError(f"Could not find config tool.track-bump in {config_path!r}")
            version = _config.get("version")
        elif config_path.suffix == ".json":
            data = json.loads(config_path.read_text())
            _config = data.get("track-bump")
            if _config is None:
                raise ValueError(f"Could not find config track-bump in {config_path}")
            version = data.get("version")
        else:
            raise ValueError("Only .toml and .json files are supported")

        if version is None:
            raise ValueError("version is required in config file")
        bump_message = _config.get("bump_message") or _config.get("bumpMessage")
        if bump_message is None:
            raise ValueError("bump_message is required in config file")

        version_files = _config.get("version_files") or _config.get("versionFiles") or []

        releases = _config.get("releases") or get_default_releases()
        config = cls(
            version=version,
            bump_message=bump_message,
            version_files=version_files,
            releases=releases,
            default_branch=default_branch,
        )
        config._config_path = config_path
        return config

    @classmethod
    def from_project(cls, project_path: Path, default_branch: str = env.DEFAULT_BRANCH):
        # Check if any of the config files exist
        for file in CONFIG_FILES:
            config_path = Path(project_path / file)
            if config_path.exists():
                logger.debug(f"Found config file: {config_path}")
                break
        else:
            raise FileNotFoundError(f"Could not find any of the following files: {CONFIG_FILES} in {project_path}")

        return cls.from_file(config_path, default_branch=default_branch)


def replace_in_files(config_path: Path, files: list[str], version: str):
    """
    Replace the version in the given files
    """
    for _file in files:
        try:
            _path, _tag = _file.split(":")
        except ValueError:
            _path = _file
            _tag = "version"
        _file_path = Path(config_path.parent / _path)
        if not _file_path.exists():
            raise FileNotFoundError(f"{_file_path} not found")
        logger.debug(f"Replacing in {_file_path}")
        replace_in_file(_file_path, version=version, tag=_tag)
