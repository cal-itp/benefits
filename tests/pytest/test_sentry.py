import os
from tempfile import NamedTemporaryFile

import pytest

from benefits import VERSION
from benefits.sentry import get_release, get_traces_sample_rate


def test_git(mocker):
    mocker.patch("benefits.sentry.git_available", return_value=True)
    mocker.patch("benefits.sentry.is_git_directory", return_value=True)

    fake_sha = "123"
    mocker.patch("benefits.sentry.get_git_revision_hash", return_value=fake_sha)

    assert get_release() == fake_sha


def test_sha_file(mocker):
    mocker.patch("benefits.sentry.git_available", return_value=True)
    mocker.patch("benefits.sentry.is_git_directory", return_value=False)

    with NamedTemporaryFile() as fp:
        fake_sha = "123"

        fp.write(bytes(fake_sha, "utf-8"))
        fp.seek(0)
        mocker.patch("benefits.sentry.get_sha_file_path", return_value=fp.name)

        assert get_release() == fake_sha


def test_no_git(mocker):
    mocker.patch("benefits.sentry.git_available", return_value=False)

    file_path = os.path.join("tmp", "nonexistent.txt")
    mocker.patch("benefits.sentry.get_sha_file_path", return_value=file_path)

    assert get_release() == VERSION


def test_git_no_repo(mocker):
    mocker.patch("benefits.sentry.git_available", return_value=True)
    mocker.patch("benefits.sentry.is_git_directory", return_value=False)

    file_path = os.path.join("tmp", "nonexistent.txt")
    mocker.patch("benefits.sentry.get_sha_file_path", return_value=file_path)

    assert get_release() == VERSION


def test_traces_sample_rate_default():
    rate = get_traces_sample_rate()
    assert rate == 0.0


@pytest.mark.parametrize("env_rate", ["0.0", "0.25", "0.99", "1.0"])
def test_traces_sample_rate_valid_range(mocker, env_rate):
    mocker.patch("benefits.sentry.os.environ.get", return_value=env_rate)

    rate = get_traces_sample_rate()
    assert rate == float(env_rate)


@pytest.mark.parametrize("env_rate", ["-1.0", "-0.1", "1.01", "2.0"])
def test_traces_sample_rate_invalid_range(mocker, env_rate):
    mocker.patch("benefits.sentry.os.environ.get", return_value=env_rate)

    with pytest.raises(ValueError, match=r"SENTRY_TRACES_SAMPLE_RATE"):
        get_traces_sample_rate()
