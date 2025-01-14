import pytest


@pytest.mark.parametrize(
    "version, expected",
    [
        pytest.param("0.1.0", ((0, 1, 0), None), id="0.1.0"),
        pytest.param("v0.1.0", ((0, 1, 0), None), id="v0.1.0"),
        pytest.param("0.1.0-beta.1", ((0, 1, 0), ("beta", 1)), id="0.1.0-beta.1"),
    ],
)
def test_parse_version(version, expected):
    from track_bump.utils import parse_version

    assert parse_version(version) == expected
