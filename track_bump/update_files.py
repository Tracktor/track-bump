import re
import tomllib
from pathlib import Path
from typing import TypedDict

from .logs import logger

__all__ = ("parse_config_file", "replace_in_file", "ParseConfig", "replace_in_files")


def replace_in_file(file_path: Path, version: str, tag: str):
    _new_test = re.sub(rf'^{tag} = "(.*)"$', rf'{tag} = "{version}"', file_path.read_text(), flags=re.MULTILINE)

    file_path.write_text(_new_test)


class ParseConfig(TypedDict):
    version: str
    bump_message: str
    version_files: list[str]


def parse_config_file(config_path: Path) -> ParseConfig:
    if not config_path.exists():
        raise FileNotFoundError(f"{config_path} not found")
    logger.debug(f"Parsing {config_path}")
    data = tomllib.loads(config_path.read_text())

    _config = data.get("tool", {}).get("track-bump")
    if _config is None:
        raise ValueError("Could not find config tool.track-bump in file_path")

    version = _config.get("version")
    if version is None:
        raise ValueError("version is required in config file")
    bump_message = _config.get("bump_message")
    if bump_message is None:
        raise ValueError("bump_message is required in config file")
    version_files = _config.get("version_files", [])
    return {"version": version, "bump_message": bump_message, "version_files": version_files}


def replace_in_files(config_path: Path, files: list[str], version: str):
    replace_in_file(config_path, version=version, tag="version")
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
