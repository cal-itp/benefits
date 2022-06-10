from django.urls import reverse

import pytest

from benefits.core import session
from benefits.eligibility.views import confirm


ROUTE_INDEX = "eligibility:index"
ROUTE_START = "eligibility:start"
ROUTE_CONFIRM = "eligibility:confirm"
ROUTE_ENROLLMENT = "enrollment:index"
TEMPLATE_CONFIRM = "eligibility/confirm.html"
TEMPLATE_UNVERIFIED = "eligibility/unverified.html"


@pytest.fixture
def mocked_oauth_token_request(mocker, app_request):
    mocker.patch("benefits.core.session.oauth_token", autospec=True, return_value="token")
    assert session.logged_in(app_request)
    return app_request


@pytest.fixture
def mocked_eligibile_request(mocked_oauth_token_request, mocked_session_eligibility):
    assert session.eligibility(mocked_oauth_token_request) == mocked_session_eligibility
    return mocked_oauth_token_request


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_index_with_agency(client):
    path = reverse(ROUTE_INDEX)
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.django_db
def test_index_without_agency(client):
    path = reverse(ROUTE_INDEX)
    with pytest.raises(AttributeError, match=r"agency"):
        client.get(path)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier")
def test_start_with_verifier(client):
    path = reverse(ROUTE_START)
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_start_without_verifier(client):
    path = reverse(ROUTE_START)
    with pytest.raises(AttributeError, match=r"verifier"):
        client.get(path)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier")
def test_confirm_get_unverified(mocked_oauth_token_request):
    response = confirm(mocked_oauth_token_request)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_verifier")
def test_confirm_get_verified(mocker, mocked_eligibile_request):
    mock = mocker.patch("benefits.eligibility.views.session.update")

    response = confirm(mocked_eligibile_request)

    assert response.status_code == 302
    assert response.url == reverse("enrollment:index")
    mock.assert_called_once()
