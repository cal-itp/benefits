from django.urls import reverse

import pytest

from benefits.core.models import TransitAgency
import benefits.core.session
from benefits.core.views import ROUTE_ELIGIBILITY, ROUTE_INDEX, ROUTE_HELP, TEMPLATE_AGENCY, bad_request, csrf_failure


ROUTE_AGENCY = "core:agency_index"


@pytest.fixture
def session_reset_spy(mocker):
    return mocker.spy(benefits.core.session, "reset")


@pytest.fixture
def mocked_active_agency(mocker):
    mock_agency = mocker.Mock()
    mock_agency.index_url = "/agency"
    mocker.patch("benefits.core.session.agency", return_value=mock_agency)
    mocker.patch("benefits.core.session.active_agency", return_value=True)
    return mock_agency


@pytest.mark.django_db
def test_index_multiple_agencies(client):
    """Assumes that fixture data contains multiple active agencies."""
    path = reverse(ROUTE_INDEX)
    response = client.get(path)

    assert response.status_code == 200
    assert "transit" in str(response.content)


@pytest.mark.django_db
def test_index_single_agency(mocker, client, session_reset_spy):
    # all_active set to ABC
    agency = TransitAgency.by_slug("abc")
    mocker.patch("benefits.core.models.TransitAgency.all_active", return_value=[agency])

    path = reverse(ROUTE_INDEX)
    response = client.get(path)

    session_reset_spy.assert_called_once()
    assert response.status_code == 302
    assert response.url == agency.index_url


@pytest.mark.django_db
def test_agency_index_single_verifier(mocker, client, session_reset_spy, mocked_session_update):
    # Agency set to DEFTl, which only has 1 verifier
    agency = TransitAgency.by_slug("deftl")
    mocker.patch("benefits.core.models.TransitAgency.all_active", return_value=[agency])

    response = client.get(agency.index_url)

    session_reset_spy.assert_called_once()
    mocked_session_update.assert_called_once()

    assert response.status_code == 302
    assert response.url == reverse(ROUTE_ELIGIBILITY)


@pytest.mark.django_db
def test_agency_index_multiple_verifier(mocker, client, session_reset_spy, mocked_session_update):
    # Agency set to ABC, which has 2 verifiers
    agency = TransitAgency.by_slug("abc")
    mocker.patch("benefits.core.models.TransitAgency.all_active", return_value=[agency])

    response = client.get(agency.index_url)

    session_reset_spy.assert_called_once()
    mocked_session_update.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_AGENCY


@pytest.mark.django_db
def test_help(client):
    path = reverse(ROUTE_HELP)

    response = client.get(path)

    assert response.status_code == 200
    assert "card" in str(response.content)


@pytest.mark.django_db
def test_help_with_session_agency(mocked_session_agency, client):
    path = reverse(ROUTE_HELP)
    response = client.get(path)

    assert response.status_code == 200
    # mocked_session_agency is Mocked version of the session.agency() function
    # call it (with a None request) to return the sample agency
    agency = mocked_session_agency(None)
    assert agency.long_name in str(response.content)


@pytest.mark.django_db
def test_bad_request_active_agency(app_request, mocked_active_agency, mocked_session_update):
    response = bad_request(app_request, Exception())

    assert response.status_code == 400
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == mocked_active_agency.index_url


@pytest.mark.django_db
def test_bad_request_no_active_agency(app_request, mocked_session_update):
    response = bad_request(app_request, Exception())

    assert response.status_code == 400
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == reverse(ROUTE_INDEX)


@pytest.mark.django_db
def test_csrf_failure_active_agency(app_request, mocked_active_agency, mocked_session_update):
    response = csrf_failure(app_request, "reason")

    assert response.status_code == 404
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == mocked_active_agency.index_url


@pytest.mark.django_db
def test_csrf_failure_no_active_agency(app_request, mocked_session_update):
    response = csrf_failure(app_request, "reason")

    assert response.status_code == 404
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == reverse(ROUTE_INDEX)


@pytest.mark.django_db
def test_not_found_active_agency(mocker, client, mocked_active_agency, mocked_session_update):
    response = client.get("/not-found")

    assert response.status_code == 404
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == mocked_active_agency.index_url


@pytest.mark.django_db
def test_not_found_no_active_agency(mocker, client, mocked_session_update):
    mocker.patch("benefits.core.session.active_agency", return_value=False)

    response = client.get("/not-found")

    assert response.status_code == 404
    assert "origin" in mocked_session_update.call_args.kwargs
    assert mocked_session_update.call_args.kwargs["origin"] == reverse(ROUTE_INDEX)
