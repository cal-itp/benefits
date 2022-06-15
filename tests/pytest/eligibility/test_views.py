from django.urls import reverse

import pytest


from benefits.eligibility.forms import EligibilityVerifierSelectionForm
from benefits.eligibility.views import (
    ROUTE_INDEX,
    ROUTE_START,
    ROUTE_LOGIN,
    ROUTE_CONFIRM,
    ROUTE_ENROLLMENT,
    TEMPLATE_PAGE,
    TEMPLATE_CONFIRM,
    TEMPLATE_UNVERIFIED,
)

import benefits.eligibility.views


@pytest.fixture
def form_data():
    return {"sub": "A1234567", "name": "Person"}


@pytest.fixture
def invalid_form_data():
    return {"invalid": "data"}


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.eligibility.views)


@pytest.fixture
def mocked_eligibility_auth_request(mocked_eligibility_request_session, mocked_session_oauth_token):
    """
    Stub fixture combines mocked_eligibility_request_session and mocked_session_oauth_token
    so that session behaves like in an authenticated request to the eligibility app
    """
    pass


@pytest.fixture
def mocked_verifier_form(mocker):
    mock_form = mocker.Mock(spec=EligibilityVerifierSelectionForm)
    mocker.patch("benefits.eligibility.views.forms.EligibilityVerifierSelectionForm", return_value=mock_form)


@pytest.fixture(autouse=True)
def disable_rate_limit(mocker):
    # override session rate limit handling for all tests
    mock_settings = mocker.patch("benefits.core.middleware.settings")
    mock_settings.RATE_LIMIT_ENABLED = False


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_index_get_agency_multiple_verifiers(mocker, first_agency, first_verifier, mocked_session_agency, client):
    # override the mocked session agency with a mock agency that has multiple verifiers
    mock_agency = mocker.Mock(spec=first_agency)
    mock_agency.eligibility_verifiers.all.return_value = [first_verifier, first_verifier]
    mock_agency.eligibility_verifiers.count.return_value = 2
    mocked_session_agency.return_value = mock_agency

    path = reverse(ROUTE_INDEX)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_PAGE
    assert "page" in response.context_data
    assert len(response.context_data["page"].forms) > 0
    assert isinstance(response.context_data["page"].forms[0], EligibilityVerifierSelectionForm)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_index_get_agency_single_verifier(mocker, first_agency, first_verifier, mocked_session_agency, client):
    # override the mocked session agency with a mock agency that has a single verifier
    mock_agency = mocker.Mock(spec=first_agency)
    mock_agency.eligibility_verifiers.all.return_value = [first_verifier]
    mock_agency.eligibility_verifiers.count.return_value = 1
    mocked_session_agency.return_value = mock_agency

    path = reverse(ROUTE_INDEX)
    response = client.get(path)

    assert response.status_code == 302
    assert response.url == reverse(ROUTE_START)


@pytest.mark.django_db
def test_index_get_without_agency(client):
    path = reverse(ROUTE_INDEX)
    with pytest.raises(AttributeError, match=r"agency"):
        client.get(path)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_index_post_invalid_form(client):
    path = reverse(ROUTE_INDEX)

    response = client.post(path, {"invalid": "data"})

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_index_post_valid_form(client, first_verifier, mocked_session_update):
    path = reverse(ROUTE_INDEX)

    response = client.post(path, {"verifier": first_verifier.id})

    assert response.status_code == 302
    assert response.url == reverse(ROUTE_START)
    assert mocked_session_update.call_args.kwargs["verifier"] == first_verifier


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_verifier_form", "mocked_session_verifier_auth_required")
def test_start_verifier_auth_required_no_oauth_client(mocker, client):
    mock_settings = mocker.patch("benefits.eligibility.views.settings")
    mock_settings.OAUTH_CLIENT_NAME = None

    path = reverse(ROUTE_START)
    with pytest.raises(Exception, match=r"OAUTH_CLIENT_NAME"):
        client.get(path)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_verifier_form", "mocked_session_verifier_auth_required")
def test_start_verifier_auth_required_logged_in(mocker, client):
    mock_session = mocker.patch("benefits.eligibility.views.session")
    mock_session.logged_in.return_value = True

    path = reverse(ROUTE_START)
    response = client.get(path)

    assert response.status_code == 200
    assert "page" in response.context_data
    assert len(response.context_data["page"].buttons) == 1
    assert response.context_data["page"].buttons[0].url == reverse(ROUTE_CONFIRM)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_verifier_form", "mocked_session_verifier_auth_required")
def test_start_verifier_auth_required_not_logged_in(mocker, client):
    mock_session = mocker.patch("benefits.eligibility.views.session")
    mock_session.logged_in.return_value = False

    path = reverse(ROUTE_START)
    response = client.get(path)

    assert response.status_code == 200
    assert "page" in response.context_data
    assert len(response.context_data["page"].buttons) == 1
    assert response.context_data["page"].buttons[0].url == reverse(ROUTE_LOGIN)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_verifier_form", "mocked_session_verifier_auth_not_required")
def test_start_verifier_auth_not_required(client):
    path = reverse(ROUTE_START)
    response = client.get(path)

    assert response.status_code == 200
    assert "page" in response.context_data
    assert len(response.context_data["page"].buttons) == 1
    assert response.context_data["page"].buttons[0].url == reverse(ROUTE_CONFIRM)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_start_without_verifier(client):
    path = reverse(ROUTE_START)
    with pytest.raises(AttributeError, match=r"verifier"):
        client.get(path)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request")
def test_confirm_get_unverified(client):
    path = reverse(ROUTE_CONFIRM)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request", "mocked_session_eligibility")
def test_confirm_get_verified(client, mocked_session_update):
    path = reverse(ROUTE_CONFIRM)
    response = client.get(path)

    assert response.status_code == 302
    assert response.url == reverse(ROUTE_ENROLLMENT)
    mocked_session_update.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request")
def test_confirm_post_invalid_form(client, invalid_form_data, mocked_analytics_module):
    path = reverse(ROUTE_CONFIRM)
    response = client.post(path, invalid_form_data)

    mocked_analytics_module.started_eligibility.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_analytics_module", "mocked_eligibility_auth_request")
def test_confirm_post_recaptcha_fail(mocker, client, invalid_form_data):
    mocker.patch("benefits.eligibility.views.recaptcha.has_error", return_value=True)
    messages = mocker.spy(benefits.eligibility.views, "messages")

    path = reverse(ROUTE_CONFIRM)
    response = client.post(path, invalid_form_data)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM
    messages.error.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request")
def test_confirm_post_valid_form_eligibility_error(mocker, client, form_data, mocked_analytics_module):
    mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=None)

    path = reverse(ROUTE_CONFIRM)
    response = client.post(path, form_data)

    mocked_analytics_module.returned_error.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request")
def test_confirm_post_valid_form_eligibility_unverified(mocker, client, form_data, mocked_analytics_module):
    mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=[])

    path = reverse(ROUTE_CONFIRM)
    response = client.post(path, form_data)

    mocked_analytics_module.returned_fail.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_UNVERIFIED


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request")
def test_confirm_post_valid_form_eligibility_verified(
    mocker, client, form_data, mocked_session_eligibility, mocked_session_update, mocked_analytics_module
):
    # mocked_session_eligibility is a fixture that mocks benefits.core.session.eligibility(request)
    # call it here, passing a None request, to get the return value from the mock
    eligibility = mocked_session_eligibility(None)
    mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=[eligibility])

    path = reverse(ROUTE_CONFIRM)
    response = client.post(path, form_data)

    mocked_session_update.assert_called_once()
    mocked_analytics_module.returned_success.assert_called_once()
    assert response.status_code == 302
    assert response.url == reverse(ROUTE_ENROLLMENT)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request")
def test_confirm_get_oauth_verified(
    mocker, client, mocked_session_eligibility, mocked_session_update, mocked_analytics_module
):
    # mocked_session_eligibility is a fixture that mocks benefits.core.session.eligibility(request)
    # call it here, passing a None request, to get the return value from the mock
    eligibility = mocked_session_eligibility(None)
    mocker.patch("benefits.eligibility.verify.eligibility_from_oauth", return_value=[eligibility])

    path = reverse(ROUTE_CONFIRM)
    response = client.get(path)

    mocked_session_update.assert_called_once()
    mocked_analytics_module.returned_success.assert_called_once()
    assert response.status_code == 302
    assert response.url == reverse(ROUTE_ENROLLMENT)
