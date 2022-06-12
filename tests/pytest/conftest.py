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
def first_eligibility(first_agency):
    eligibility = first_agency.eligibility_types.first()
    assert eligibility
    return eligibility


@pytest.fixture
def first_verifier(first_agency):
    verifier = first_agency.eligibility_verifiers.first()
    assert verifier
    return verifier


@pytest.fixture
def mocked_session_agency(mocker, first_agency):
    return mocker.patch("benefits.core.session.agency", autospec=True, return_value=first_agency)


@pytest.fixture
def mocked_session_eligibility(mocker, first_eligibility):
    mocker.patch("benefits.core.session.eligible", autospec=True, return_value=True)
    return mocker.patch("benefits.core.session.eligibility", autospec=True, return_value=first_eligibility)


@pytest.fixture
def mocked_session_oauth_token(mocker):
    return mocker.patch("benefits.core.session.oauth_token", autospec=True, return_value="token")


@pytest.fixture
def mocked_session_verifier(mocker, first_verifier):
    return mocker.patch("benefits.core.session.verifier", autospec=True, return_value=first_verifier)


@pytest.fixture
def mocked_session_verifier_auth_required(mocker, first_verifier, mocked_session_verifier):
    mock_verifier = mocker.Mock(spec=first_verifier)
    mock_verifier.requires_authentication = True
    mocked_session_verifier.return_value = mock_verifier
    return mocked_session_verifier


@pytest.fixture
def mocked_session_verifier_auth_not_required(mocked_session_verifier_auth_required):
    # mocked_session_verifier_auth_required.return_value is the Mock(spec=first_verifier) from that fixture
    mocked_session_verifier_auth_required.return_value.requires_authentication = False
    return mocked_session_verifier_auth_required


@pytest.fixture
def mocked_session_update(mocker):
    return mocker.patch("benefits.eligibility.views.session.update")
