from benefits import VERSION
from benefits.sentry import get_release


def test_git(mocker):
    mocker.patch("benefits.sentry.git_available", return_value=True)
    mocker.patch("benefits.sentry.is_git_directory", return_value=True)

    fake_sha = "123"
    mocker.patch("benefits.sentry.get_git_revision_hash", return_value=fake_sha)

    assert get_release() == fake_sha


def test_sha_file(mocker):
    mocker.patch("benefits.sentry.git_available", return_value=True)
    mocker.patch("benefits.sentry.is_git_directory", return_value=False)

    fake_sha = "123"
    mocker.patch("benefits.sentry.get_sha_from_file", return_value=fake_sha)

    assert get_release() == fake_sha


def test_no_git(mocker):
    mocker.patch("benefits.sentry.git_available", return_value=False)
    mocker.patch("benefits.sentry.get_sha_from_file", return_value=None)

    assert get_release() == VERSION


def test_git_no_repo(mocker):
    mocker.patch("benefits.sentry.git_available", return_value=True)
    mocker.patch("benefits.sentry.is_git_directory", return_value=False)
    mocker.patch("benefits.sentry.get_sha_from_file", return_value=None)

    assert get_release() == VERSION
