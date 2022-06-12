from django.urls import reverse

import pytest

from benefits.core.models import TransitAgency
import benefits.core.session


ROUTE_INDEX = "core:index"
ROUTE_AGENCY_INDEX = "core:agency_index"
ROUTE_HELP = "core:help"
TEMPLATE_AGENCY = "core/agency_index.html"


@pytest.fixture
def session_reset_spy(mocker):
    return mocker.spy(benefits.core.session, "reset")


@pytest.mark.django_db
def test_index_multiple_agencies(client):
    """Assumes that fixture data contains multiple active agencies."""
    path = reverse(ROUTE_INDEX)
    response = client.get(path)

    assert response.status_code == 200
    assert "transit" in str(response.content)


@pytest.mark.django_db
def test_index_single_agency(mocker, client, session_reset_spy):
    agencies = TransitAgency.all_active()[:1]
    mocker.patch("benefits.core.models.TransitAgency.all_active", return_value=agencies)

    path = reverse(ROUTE_INDEX)
    response = client.get(path)

    assert response.status_code == 302
    assert response.url == agencies[0].index_url
    session_reset_spy.assert_called_once()


@pytest.mark.django_db
def test_agency_index(first_agency, client, session_reset_spy):
    path = reverse(ROUTE_AGENCY_INDEX, kwargs={"agency": first_agency.slug})
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_AGENCY
    session_reset_spy.assert_called_once()


@pytest.mark.django_db
def test_homepage_single_agency_single_verifier(mocker, client):
    # Agency set to DEFTl, which only has 1 verifier
    agencies = TransitAgency.all_active()[1:]
    mocker.patch("benefits.core.models.TransitAgency.all_active", return_value=agencies)

    response = client.get(reverse("core:index"), follow=True)

    # Setting follow to True allows the test to go thorugh redirects and returns the redirect_chain attr
    # https://docs.djangoproject.com/en/3.2/topics/testing/tools/#making-requests
    assert response.redirect_chain[0] == ("/deftl", 302)
    assert response.redirect_chain[1] == ("/eligibility/", 302)
    assert response.redirect_chain[-1] == ("/eligibility/start", 302)


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
def test_not_found_active_agency(mocker, client):
    mock_agency = mocker.Mock()
    mock_agency.index_url = "/agency"
    mocker.patch("benefits.core.session.agency", return_value=mock_agency)
    mocker.patch("benefits.core.session.active_agency", return_value=True)
    spy_session_update = mocker.spy(benefits.core.session, "update")

    response = client.get("/not-found")

    assert response.status_code == 404
    assert "origin" in spy_session_update.call_args.kwargs
    assert spy_session_update.call_args.kwargs["origin"] == mock_agency.index_url


@pytest.mark.django_db
def test_not_found_no_active_agency(mocker, client):
    mocker.patch("benefits.core.session.active_agency", return_value=False)
    spy_session_update = mocker.spy(benefits.core.session, "update")

    response = client.get("/not-found")

    assert response.status_code == 404
    assert "origin" in spy_session_update.call_args.kwargs
    assert spy_session_update.call_args.kwargs["origin"] == reverse("core:index")
