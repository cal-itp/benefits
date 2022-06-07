from unittest.mock import create_autospec
from django.contrib.sessions.middleware import SessionMiddleware
from django.middleware.locale import LocaleMiddleware

import pytest
from pytest_socket import disable_socket

from benefits.core import session
from benefits.core.models import TransitAgency


def pytest_runtest_setup():
    disable_socket()


@pytest.fixture(scope="session")
def django_db_setup():
    # use existing database since it's read-only
    pass


@pytest.fixture
def app_request(request, rf):
    """
    Fixture creates and initializes a new Django request object similar to a real application request.

    Optionally use @pytest.mark.request_path(path: str) to customize the request's path.
    """

    # see if a request_path was provided via marker
    marker = request.node.get_closest_marker("request_path")
    request_path = marker.args[0] if marker else "/some/arbitrary/path"

    # create a request for the path, initialize
    app_request = rf.get(request_path)
    initialize_request(app_request)

    return app_request


@pytest.fixture
def mocked_view():
    def test_view(request):
        pass

    return create_autospec(test_view)


def initialize_request(request):
    """Helper initializes a Django request object with session and language information."""

    # https://stackoverflow.com/a/55530933/358804
    middleware = [SessionMiddleware(lambda x: x), LocaleMiddleware(lambda x: x)]

    for m in middleware:
        m.process_request(request)

    request.session.save()

    session.reset(request)


def set_agency(mocker):
    agency = TransitAgency.objects.first()
    assert agency
    with_agency(mocker, agency)
    return agency


def set_verifier(mocker):
    agency = set_agency(mocker)

    mock = mocker.patch("benefits.core.session.verifier", autospec=True)
    verifier = agency.eligibility_verifiers.first()
    mocker.patch.object(verifier, "api_url", "http://localhost/verify")
    assert verifier
    mock.return_value = verifier
    return (agency, verifier)


def with_agency(mocker, agency):
    mocker.patch("benefits.core.session.agency", autospec=True, return_value=agency)
