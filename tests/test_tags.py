from contextlib import nullcontext

import pytest

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
def test_get_branch_release(branch, expected):
    from track_bump.tags import get_branch_release

    with expected as e:
        assert get_branch_release(branch) == e


@pytest.mark.parametrize(
    "params, expected",
    [
        pytest.param(
            {"stable_tag": "v0.1.0", "release_tag": None, "release": "beta"}, nullcontext("v0.2.0-beta.0"), id="beta"
        ),
        pytest.param(
            {"stable_tag": "v0.1.0", "release_tag": "v0.2.0-beta.1", "release": "beta"},
            nullcontext("v0.2.0-beta.2"),
            id="beta existing release tag",
        ),
        pytest.param(
            {"stable_tag": "v0.1.0", "release_tag": None, "release": "stable"},
            nullcontext("v0.2.0"),
            id="stable",
        ),
        pytest.param(
            {
                "stable_tag": "v0.1.0",
                "release_tag": None,
                "release": "stable",
                "last_commit_message": "release: v0.1.0",
            },
            nullcontext("v0.2.0"),
            id="stable with commit message",
        ),
        pytest.param(
            {"stable_tag": "v0.1.0", "release_tag": None, "release": "stable", "last_commit_message": "fix: v0.1.0"},
            nullcontext("v0.1.1"),
            id="stable patch with commit message",
        ),
    ],
)
def test_get_new_tag(params, expected):
    from track_bump.tags import get_new_tag

    with expected as e:
        assert get_new_tag(**params) == e
