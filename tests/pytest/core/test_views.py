import pytest
from django.urls import reverse
from benefits.core.models import TransitAgency


@pytest.mark.django_db
def test_homepage_multiple_agencies(client):
    """Assumes that fixture data contains multiple active agencies."""
    path = reverse("core:index")
    response = client.get(path)
    assert response.status_code == 200
    assert "transit" in str(response.content)


@pytest.mark.django_db
def test_homepage_single_agency(mocker, client):
    agencies = TransitAgency.all_active()[:1]
    mocker.patch("benefits.core.models.TransitAgency.all_active", return_value=agencies)
    path = reverse("core:index")
    response = client.get(path)
    assert response.status_code == 302
    assert response.url == agencies[0].index_url


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
    path = reverse("core:help")
    response = client.get(path)
    assert response.status_code == 200
    assert "card" in str(response.content)


@pytest.mark.django_db
def test_help_with_agency(mocked_session_agency, client):
    path = reverse("core:help")
    response = client.get(path)
    assert response.status_code == 200
    # mocked_session_agency is Mocked version of the session.agency() function
    # call it (with a None request) to return the sample agency
    agency = mocked_session_agency(None)
    assert agency.long_name in str(response.content)
