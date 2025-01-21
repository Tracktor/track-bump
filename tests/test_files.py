import textwrap
import tomllib
from contextlib import nullcontext

import pytest


@pytest.mark.parametrize(
    "filename, config, expected",
    [
        # TOML
        pytest.param(
            "pyproject.toml",
            """
            [tool.track-bump]
            version = "0.1.0"
            bump_message = "foo"
            """,
            nullcontext({"version": "0.1.0", "bump_message": "foo", "version_files": []}),
            id="toml - valid config",
        ),
        pytest.param(
            "pyproject.toml",
            """
            foo
            """,
            pytest.raises(tomllib.TOMLDecodeError),
            id="toml - invalid file",
        ),
        pytest.param(
            "pyproject.toml",
            """
            [tool.track-bump]
            version = "0.1.0"
            """,
            pytest.raises(ValueError, match="bump_message is required in config file"),
            id="toml - missing bump_message",
        ),
        pytest.param(
            "pyproject.toml",
            """
            [tool.track-bump]
            bump_message = "foo"
            """,
            pytest.raises(ValueError, match="version is required in config file"),
            id="toml - missing version",
        ),
        pytest.param(
            "pyproject.toml",
            """
            [tool.track-bump]
            version = "0.1.0"
            bump_message = "foo"
            version_files = ["pyproject.toml"]
            """,
            nullcontext({"version": "0.1.0", "bump_message": "foo", "version_files": ["pyproject.toml"]}),
            id="toml - valid config with version_files",
        ),
        # JSON
        pytest.param(
            "package.json",
            """
            {
                "version": "0.1.0",
                "track-bump": {
                    "bumpMessage": "foo"
                }
            }
            """,
            nullcontext({"version": "0.1.0", "bump_message": "foo", "version_files": []}),
            id="json - valid config",
        ),
        pytest.param(
            "package.json",
            """
            {
                "version": "0.1.0",
                "track-bump": {
                }
            }
            """,
            pytest.raises(ValueError, match="bump_message is required in config file"),
            id="json - missing bump_message",
        ),
    ],
)
def test_load_config(tmp_path, filename, config, expected):
    from track_bump.config import Config

    _path = tmp_path / filename
    _path.write_text(config)
    with expected as e:
        _config = Config.from_file(_path)
        assert _config.version == e["version"]
        assert _config.bump_message == e["bump_message"]
        assert _config.version_files == e["version_files"]


@pytest.mark.parametrize(
    "filename, file_content,params,expected",
    [
        pytest.param(
            "pyproject.toml",
            """
            [tool.track-bump]
            version = "0.1.0"
            bump_message = "foo"
            """,
            {"version": "0.2.0", "tag": "version"},
            """
            [tool.track-bump]
            version = "0.2.0"
            bump_message = "foo"
            """,
            id="toml - valid",
        ),
        pytest.param(
            "package.json",
            """
            {
                "version": "0.1.0",
                "track-bump": {
                    "bumpMessage": "foo"
                }
            }
            """,
            {"version": "0.2.0", "tag": "version"},
            """
            {
                "version": "0.2.0",
                "track-bump": {
                    "bumpMessage": "foo"
                }
            }
            """,
            id="json - valid",
        ),
    ],
)
def test_replace_in_file(tmp_path, filename, expected, file_content, params):
    from track_bump.config import replace_in_file

    _path = tmp_path / filename
    _path.write_text(textwrap.dedent(file_content))

    replace_in_file(_path, **params)

    assert _path.read_text() == textwrap.dedent(expected)
