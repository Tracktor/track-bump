import textwrap
import tomllib
from contextlib import nullcontext

import pytest


@pytest.mark.parametrize(
    "config, expected",
    [
        pytest.param(
            """
            [tool.track-bump]
            version = "0.1.0"
            bump_message = "foo"
            """,
            nullcontext({"version": "0.1.0", "bump_message": "foo", "version_files": []}),
            id="valid config",
        ),
        pytest.param(
            """
            foo
            """,
            pytest.raises(tomllib.TOMLDecodeError),
            id="invalid file",
        ),
        pytest.param(
            """
            [tool.track-bump]
            version = "0.1.0"
            """,
            pytest.raises(ValueError, match="bump_message is required in config file"),
            id="missing bump_message",
        ),
        pytest.param(
            """
            [tool.track-bump]
            bump_message = "foo"
            """,
            pytest.raises(ValueError, match="version is required in config file"),
            id="missing version",
        ),
        pytest.param(
            """
            [tool.track-bump]
            version = "0.1.0"
            bump_message = "foo"
            version_files = ["pyproject.toml"]
            """,
            nullcontext({"version": "0.1.0", "bump_message": "foo", "version_files": ["pyproject.toml"]}),
            id="valid config with version_files",
        ),
    ],
)
def test_parse_config_file(tmp_path, config, expected):
    from track_bump.update_files import parse_config_file

    _path = tmp_path / "pyproject.toml"
    _path.write_text(config)
    with expected as e:
        assert parse_config_file(_path) == e


@pytest.mark.parametrize(
    "file_content,params,expected",
    [
        pytest.param(
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
            id="valid",
        )
    ],
)
def test_replace_in_file(tmp_path, expected, file_content, params):
    from track_bump.update_files import replace_in_file

    _path = tmp_path / "pyproject.toml"
    _path.write_text(textwrap.dedent(file_content))

    replace_in_file(_path, **params)

    assert _path.read_text() == textwrap.dedent(expected)
