import time

import pytest
from authlib.integrations.base_client.errors import UnsupportedTokenTypeError
from django.urls import reverse
from requests import HTTPError
from unittest.mock import patch, PropertyMock


from benefits.core import models
from benefits.enrollment.enrollment import Status
from benefits.enrollment_littlepay.enrollment import CardTokenizationAccessResponse
import benefits.in_person.views
from benefits.routes import routes


@pytest.fixture
def card_tokenize_form_data():
    return {"card_token": "tokenized_card"}


@pytest.fixture
def invalid_form_data():
    return {"invalid": "data"}


@pytest.fixture
def mocked_eligibility_analytics_module(mocker):
    return mocker.patch.object(benefits.in_person.views, "eligibility_analytics")


@pytest.fixture
def mocked_enrollment_analytics_module(mocker):
    return mocker.patch.object(benefits.in_person.views, "enrollment_analytics")


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.in_person.views, "sentry_sdk")


@pytest.mark.django_db
@pytest.mark.parametrize("viewname", [routes.IN_PERSON_ELIGIBILITY, routes.IN_PERSON_ENROLLMENT])
def test_view_not_logged_in(client, viewname):
    path = reverse(viewname)

    response = client.get(path)
    assert response.status_code == 302
    assert response.url == "/admin/login/?next=" + path


# admin_client is a fixture from pytest
# https://pytest-django.readthedocs.io/en/latest/helpers.html#admin-client-django-test-client-logged-in-as-admin
@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_eligibility_logged_in(admin_client):
    path = reverse(routes.IN_PERSON_ELIGIBILITY)

    response = admin_client.get(path)
    assert response.status_code == 200
    assert response.template_name == "in_person/eligibility.html"


@pytest.mark.django_db
def test_eligibility_logged_in_filtering_flows(mocker, model_TransitAgency, admin_client):
    digital = models.EnrollmentFlow.objects.create(
        transit_agency=model_TransitAgency, supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL], label="Digital"
    )
    in_person = models.EnrollmentFlow.objects.create(
        transit_agency=model_TransitAgency,
        supported_enrollment_methods=[models.EnrollmentMethods.IN_PERSON],
        label="In-Person",
    )
    both = models.EnrollmentFlow.objects.create(
        transit_agency=model_TransitAgency,
        supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL, models.EnrollmentMethods.IN_PERSON],
        label="Both",
    )
    mocker.patch("benefits.core.session.agency", autospec=True, return_value=model_TransitAgency)

    path = reverse(routes.IN_PERSON_ELIGIBILITY)
    response = admin_client.get(path)
    filtered_flow_ids = [choice[0] for choice in response.context_data["form"].fields["flow"].choices]

    assert in_person.id, both.id in filtered_flow_ids
    assert digital.id not in filtered_flow_ids


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow")
def test_eligibility_post_no_flow_selected(admin_client):

    path = reverse(routes.IN_PERSON_ELIGIBILITY)
    form_data = {}
    response = admin_client.post(path, form_data)

    # should return user back to the in-person eligibility index
    assert response.status_code == 200
    assert response.template_name == "in_person/eligibility.html"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow")
def test_eligibility_post_flow_selected_and_verified(
    admin_client, model_EnrollmentFlow, mocked_session_update, mocked_eligibility_analytics_module
):

    path = reverse(routes.IN_PERSON_ELIGIBILITY)
    form_data = {"flow": 1, "verified_1": True}
    response = admin_client.post(path, form_data)

    assert response.status_code == 302
    assert response.url == reverse(routes.IN_PERSON_ENROLLMENT)
    assert mocked_session_update.call_args.kwargs["flow"] == model_EnrollmentFlow
    mocked_eligibility_analytics_module.selected_flow.assert_called_once()
    mocked_eligibility_analytics_module.started_eligibility.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow")
def test_eligibility_post_flow_selected_and_unverified(admin_client):

    path = reverse(routes.IN_PERSON_ELIGIBILITY)
    form_data = {"flow": 1, "verified_1": False}
    response = admin_client.post(path, form_data)

    # should return user back to the in-person eligibility index
    assert response.status_code == 200
    assert response.template_name == "in_person/eligibility.html"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_refresh(mocker, admin_client):
    mocker.patch("benefits.enrollment_littlepay.session.Session.access_token_valid", return_value=False)

    mock_token = {}
    mock_token["access_token"] = "access_token"
    mock_token["expires_at"] = time.time() + 10000

    mocker.patch(
        "benefits.in_person.views.request_card_tokenization_access",
        return_value=CardTokenizationAccessResponse(
            Status.SUCCESS,
            access_token=mock_token["access_token"],
            expires_at=mock_token["expires_at"],
        ),
    )

    path = reverse(routes.IN_PERSON_ENROLLMENT_TOKEN)
    response = admin_client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"] == mock_token["access_token"]


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
@patch("benefits.enrollment_littlepay.session.Session.access_token", new=PropertyMock(return_value="enrollment_token"))
def test_token_valid(mocker, admin_client):
    mocker.patch("benefits.enrollment_littlepay.session.Session.access_token_valid", return_value=True)

    path = reverse(routes.IN_PERSON_ENROLLMENT_TOKEN)
    response = admin_client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"] == "enrollment_token"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_system_error(mocker, admin_client, mocked_enrollment_analytics_module, mocked_sentry_sdk_module):
    mocker.patch("benefits.enrollment_littlepay.session.Session.access_token_valid", return_value=False)

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=500, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(response=mock_error_response)

    mocker.patch(
        "benefits.in_person.views.request_card_tokenization_access",
        return_value=CardTokenizationAccessResponse(
            Status.SYSTEM_ERROR, access_token=None, expires_at=None, exception=http_error, status_code=500
        ),
    )

    path = reverse(routes.IN_PERSON_ENROLLMENT_TOKEN)
    response = admin_client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" not in data
    assert "redirect" in data
    assert data["redirect"] == reverse(routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR)
    mocked_enrollment_analytics_module.failed_pretokenization_request.assert_called_once()
    assert 500 in mocked_enrollment_analytics_module.failed_pretokenization_request.call_args.args
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_http_error_400(mocker, admin_client, mocked_enrollment_analytics_module, mocked_sentry_sdk_module):
    mocker.patch("benefits.enrollment_littlepay.session.Session.access_token_valid", return_value=False)

    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=400, **mock_error)
    mock_error_response.json.return_value = mock_error
    http_error = HTTPError(response=mock_error_response)

    mocker.patch(
        "benefits.in_person.views.request_card_tokenization_access",
        return_value=CardTokenizationAccessResponse(
            Status.EXCEPTION, access_token=None, expires_at=None, exception=http_error, status_code=400
        ),
    )

    path = reverse(routes.IN_PERSON_ENROLLMENT_TOKEN)
    response = admin_client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" not in data
    assert "redirect" in data
    assert data["redirect"] == reverse(routes.IN_PERSON_SERVER_ERROR)
    mocked_enrollment_analytics_module.failed_pretokenization_request.assert_called_once()
    assert 400 in mocked_enrollment_analytics_module.failed_pretokenization_request.call_args.args
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_misconfigured_client_id(mocker, admin_client, mocked_enrollment_analytics_module, mocked_sentry_sdk_module):
    mocker.patch("benefits.enrollment_littlepay.session.Session.access_token_valid", return_value=False)

    exception = UnsupportedTokenTypeError()

    mocker.patch(
        "benefits.in_person.views.request_card_tokenization_access",
        return_value=CardTokenizationAccessResponse(
            Status.EXCEPTION, access_token=None, expires_at=None, exception=exception, status_code=None
        ),
    )

    path = reverse(routes.IN_PERSON_ENROLLMENT_TOKEN)
    response = admin_client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" not in data
    assert "redirect" in data
    assert data["redirect"] == reverse(routes.IN_PERSON_SERVER_ERROR)
    mocked_enrollment_analytics_module.failed_pretokenization_request.assert_called_once()
    mocked_sentry_sdk_module.capture_exception_assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_token_connection_error(mocker, admin_client, mocked_enrollment_analytics_module, mocked_sentry_sdk_module):
    mocker.patch("benefits.enrollment_littlepay.session.Session.access_token_valid", return_value=False)

    exception = ConnectionError()

    mocker.patch(
        "benefits.in_person.views.request_card_tokenization_access",
        return_value=CardTokenizationAccessResponse(
            Status.EXCEPTION, access_token=None, expires_at=None, exception=exception, status_code=None
        ),
    )

    path = reverse(routes.IN_PERSON_ENROLLMENT_TOKEN)
    response = admin_client.get(path)

    assert response.status_code == 200
    data = response.json()
    assert "token" not in data
    assert "redirect" in data
    assert data["redirect"] == reverse(routes.IN_PERSON_SERVER_ERROR)
    mocked_enrollment_analytics_module.failed_pretokenization_request.assert_called_once()
    mocked_sentry_sdk_module.capture_exception_assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "model_LittlepayConfig")
def test_enrollment_logged_in_get(admin_client):
    path = reverse(routes.IN_PERSON_ENROLLMENT)

    response = admin_client.get(path)
    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment/index.html"
    assert "forms" in response.context_data
    assert "cta_button" in response.context_data
    assert "token_field" in response.context_data
    assert "form_retry" in response.context_data
    assert "form_success" in response.context_data
    assert "card_types" in response.context_data

    # not supporting internationalization in in_person app yet
    assert "overlay_language" not in response.context_data


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_enrollment_post_invalid_form(admin_client, invalid_form_data):
    path = reverse(routes.IN_PERSON_ENROLLMENT)

    with pytest.raises(Exception, match=r"form"):
        admin_client.post(path, invalid_form_data)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "model_EnrollmentFlow", "model_LittlepayGroup")
def test_enrollment_post_valid_form_success(
    mocker,
    admin_client,
    card_tokenize_form_data,
    mocked_eligibility_analytics_module,
    mocked_enrollment_analytics_module,
    model_TransitAgency,
    model_EnrollmentFlow,
    model_User,
):
    mocker.patch("benefits.in_person.views.enroll", return_value=(Status.SUCCESS, None))
    spy = mocker.spy(benefits.in_person.views.models.EnrollmentEvent.objects, "create")

    # force the model_User to be the logged in user
    # e.g. the TransitAgency staff person assisting this in-person enrollment
    admin_client.force_login(model_User)

    path = reverse(routes.IN_PERSON_ENROLLMENT)
    response = admin_client.post(path, card_tokenize_form_data)

    spy.assert_called_once_with(
        transit_agency=model_TransitAgency,
        enrollment_flow=model_EnrollmentFlow,
        enrollment_method=models.EnrollmentMethods.IN_PERSON,
        verified_by=f"{model_User.first_name} {model_User.last_name}",
        expiration_datetime=None,
    )

    assert response.status_code == 302
    assert response.url == reverse(routes.IN_PERSON_ENROLLMENT_SUCCESS)
    mocked_eligibility_analytics_module.returned_success.assert_called_once()
    mocked_enrollment_analytics_module.returned_success.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "model_EnrollmentFlow")
def test_enrollment_post_valid_form_system_error(
    mocker, admin_client, card_tokenize_form_data, mocked_enrollment_analytics_module, mocked_sentry_sdk_module
):
    mocker.patch("benefits.in_person.views.enroll", return_value=(Status.SYSTEM_ERROR, None))

    path = reverse(routes.IN_PERSON_ENROLLMENT)
    response = admin_client.post(path, card_tokenize_form_data)

    assert response.status_code == 302
    assert response.url == reverse(routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR)
    mocked_enrollment_analytics_module.returned_error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "model_EnrollmentFlow")
def test_enrollment_post_valid_form_exception(
    mocker, admin_client, card_tokenize_form_data, mocked_enrollment_analytics_module, mocked_sentry_sdk_module
):
    mocker.patch("benefits.in_person.views.enroll", return_value=(Status.EXCEPTION, None))

    path = reverse(routes.IN_PERSON_ENROLLMENT)
    response = admin_client.post(path, card_tokenize_form_data)

    assert response.status_code == 302
    assert response.url == reverse(routes.IN_PERSON_SERVER_ERROR)
    mocked_enrollment_analytics_module.returned_error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "model_EnrollmentFlow")
def test_enrollment_post_valid_form_reenrollment_error(
    mocker, admin_client, card_tokenize_form_data, mocked_enrollment_analytics_module
):
    mocker.patch("benefits.in_person.views.enroll", return_value=(Status.REENROLLMENT_ERROR, None))

    path = reverse(routes.IN_PERSON_ENROLLMENT)
    response = admin_client.post(path, card_tokenize_form_data)

    assert response.status_code == 302
    assert response.url == reverse(routes.IN_PERSON_ENROLLMENT_REENROLLMENT_ERROR)
    mocked_enrollment_analytics_module.returned_error.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow", "mocked_session_agency")
def test_reenrollment_error(admin_client):
    path = reverse(routes.IN_PERSON_ENROLLMENT_REENROLLMENT_ERROR)

    response = admin_client.get(path)

    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment/reenrollment_error.html"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow", "mocked_session_agency")
def test_retry(admin_client, mocked_enrollment_analytics_module):
    path = reverse(routes.IN_PERSON_ENROLLMENT_RETRY)

    response = admin_client.get(path)

    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment/retry.html"
    mocked_enrollment_analytics_module.returned_retry.assert_not_called()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow", "mocked_session_agency")
def test_retry_post(admin_client, mocked_enrollment_analytics_module):
    path = reverse(routes.IN_PERSON_ENROLLMENT_RETRY)

    response = admin_client.post(path)

    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment/retry.html"
    mocked_enrollment_analytics_module.returned_retry.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow", "mocked_session_agency")
def test_system_error(admin_client):
    path = reverse(routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR)

    response = admin_client.get(path)

    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment/system_error.html"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow", "mocked_session_agency")
def test_server_error(admin_client):
    path = reverse(routes.IN_PERSON_SERVER_ERROR)

    response = admin_client.get(path)

    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment/server_error.html"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow", "mocked_session_agency")
def test_success(admin_client):
    path = reverse(routes.IN_PERSON_ENROLLMENT_SUCCESS)

    response = admin_client.get(path)

    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment/success.html"
