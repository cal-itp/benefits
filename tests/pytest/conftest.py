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
def app_request(rf, initialize_request):
    """
    Fixture creates and initializes a new Django request object similar to a real application request.
    """
    # create a request for the path, initialize
    app_request = rf.get("/some/arbitrary/path")

    initialize_request(app_request)

    return app_request


@pytest.fixture
def initialize_request():
    """
    Fixture returns a helper function to initialize a Django request object with session and language information.
    """
    # https://stackoverflow.com/a/55530933/358804
    middleware = [SessionMiddleware(lambda x: x), LocaleMiddleware(lambda x: x)]

    def init(request):
        for m in middleware:
            m.process_request(request)

        request.session.save()

        session.reset(request)

    return init


@pytest.fixture
def mocked_analytics_module(mocker):
    """
    Fixture returns a helper function to mock the analytics module imported on another given module.
    """

    def mock(module):
        return mocker.patch.object(module, "analytics")

    return mock


@pytest.fixture
def mocked_view():
    def test_view(request):
        pass

    return create_autospec(test_view)


@pytest.fixture
def first_agency():
    agency = TransitAgency.objects.first()
    assert agency
    return agency


@pytest.fixture
def mocked_session_agency(mocker, first_agency):
    mocker.patch("benefits.core.session.agency", autospec=True, return_value=first_agency)
    return first_agency


@pytest.fixture
def mocked_session_eligibility(mocker, mocked_session_agency):
    eligibility = mocked_session_agency.eligibility_types.first()
    assert eligibility
    mocker.patch("benefits.core.session.eligibility", autospec=True, return_value=eligibility)
    return eligibility


@pytest.fixture
def mocked_session_verifier(mocker, mocked_session_agency):
    mock = mocker.patch("benefits.core.session.verifier", autospec=True)
    verifier = mocked_session_agency.eligibility_verifiers.first()
    assert verifier
    mocker.patch.object(verifier, "api_url", "http://localhost/verify")
    mock.return_value = verifier
    return (mocked_session_agency, verifier)
