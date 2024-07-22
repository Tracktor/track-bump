import pytest
from contextlib import nullcontext
from .conftest import DEFAULT_BRANCH


@pytest.mark.parametrize(
    "branch, expected",
    [
        pytest.param("develop", nullcontext("beta"), id="develop"),
        pytest.param(DEFAULT_BRANCH, nullcontext("stable"), id="main branch"),
        pytest.param("release/foo", nullcontext("rc"), id="release"),
        pytest.param("foo", pytest.raises(ValueError, match="Branch 'foo' is not supported"), id="invalid branch"),
    ],
)
def test_get_branch_release_tag(branch, expected):
    from track_bump.tags import get_branch_release_tag

    with expected as e:
        assert get_branch_release_tag(branch) == e


@pytest.mark.parametrize(
    "params, latest_release_tag, expected",
    [
        pytest.param({"latest_tag": "v0.1.0", "release_tag": "beta"}, None, nullcontext("v0.2.0-beta.0"), id="beta"),
        pytest.param(
            {"latest_tag": "v0.1.0", "release_tag": "beta"},
            "v0.2.0-beta.1",
            nullcontext("v0.2.0-beta.2"),
            id="beta existing release tag",
        ),
        pytest.param(
            {"latest_tag": None, "release_tag": "stable"},
            NotImplementedError("Should not trigger"),
            pytest.raises(ValueError, match=r"No tags found. Please create a release tag first \(like v0.1.0\)"),
            id="stable no previous",
        ),
        pytest.param(
            {"latest_tag": "v0.1.0", "release_tag": "stable"},
            NotImplementedError("Should not trigger"),
            nullcontext("v0.2.0"),
            id="stable",
        ),
    ],
)
def test_get_new_tag(params, latest_release_tag, expected, monkeypatch):
    monkeypatch.setattr("track_bump.tags.get_latest_release_tag", lambda x: latest_release_tag)
    from track_bump.tags import get_new_tag

    with expected as e:
        assert get_new_tag(**params) == e
