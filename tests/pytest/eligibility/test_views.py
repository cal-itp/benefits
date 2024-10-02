from django.urls import reverse

import pytest

from benefits.core import models
from benefits.routes import routes
from benefits.core.middleware import TEMPLATE_USER_ERROR
import benefits.core.session
from benefits.eligibility.forms import EnrollmentFlowSelectionForm, EligibilityVerificationForm
from benefits.eligibility.views import TEMPLATE_CONFIRM

import benefits.eligibility.views


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
def session_logout_spy(mocker):
    return mocker.spy(benefits.core.session, "logout")


@pytest.fixture
def mocked_flow_selection_form(mocker):
    mock_form = mocker.Mock(spec=EnrollmentFlowSelectionForm)
    mocker.patch("benefits.eligibility.views.forms.EnrollmentFlowSelectionForm", return_value=mock_form)


@pytest.fixture
def form_data():
    return {"sub": "A1234567", "name": "Person"}


@pytest.fixture
def invalid_form_data():
    return {"invalid": "data"}


class SampleVerificationForm(EligibilityVerificationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(
            "title",
            "headline",
            "blurb",
            "name_label",
            "name_placeholder",
            "name_help_text",
            "sub_label",
            "sub_placeholder",
            "sub_help_text",
            *args,
            **kwargs,
        )


@pytest.fixture
def model_EnrollmentFlow_with_form_class(mocker, model_EnrollmentFlow):
    model_EnrollmentFlow.eligibility_form_class = f"{__name__}.SampleVerificationForm"
    model_EnrollmentFlow.save()
    mocker.patch("benefits.eligibility.views.session.flow", return_value=model_EnrollmentFlow)
    return model_EnrollmentFlow


@pytest.mark.django_db
def test_index_filtering_flows(mocker, model_TransitAgency, client):
    digital = models.EnrollmentFlow.objects.create(
        transit_agency=model_TransitAgency,
        supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL],
        label="Digital",
        selection_label_template="eligibility/includes/selection-label.html",
    )
    in_person = models.EnrollmentFlow.objects.create(
        transit_agency=model_TransitAgency,
        supported_enrollment_methods=[models.EnrollmentMethods.IN_PERSON],
        label="In-Person",
        selection_label_template="eligibility/includes/selection-label.html",
    )
    both = models.EnrollmentFlow.objects.create(
        transit_agency=model_TransitAgency,
        supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL, models.EnrollmentMethods.IN_PERSON],
        label="Both",
        selection_label_template="eligibility/includes/selection-label.html",
    )
    mocker.patch("benefits.core.session.agency", autospec=True, return_value=model_TransitAgency)

    path = reverse(routes.ELIGIBILITY_INDEX)
    response = client.get(path)
    filtered_flow_ids = [choice[0] for choice in response.context_data["form"].fields["flow"].choices]

    assert digital.id, both.id in filtered_flow_ids
    assert in_person.id not in filtered_flow_ids


@pytest.mark.django_db
def test_index_get_agency_multiple_flows(mocker, model_TransitAgency, model_EnrollmentFlow, mocked_session_agency, client):
    # override the mocked session agency with a mock agency that has multiple flows
    mock_agency = mocker.Mock(spec=model_TransitAgency)

    # mock the enrollment_flows property on the class - https://stackoverflow.com/a/55642462
    mock_manager = mocker.Mock()
    mock_manager.all.return_value = [model_EnrollmentFlow, model_EnrollmentFlow]
    type(mock_agency).enrollment_flows = mocker.PropertyMock(return_value=mock_manager)
    type(mock_agency).enrollment_flows.filter.return_value = [model_EnrollmentFlow, model_EnrollmentFlow]

    mock_agency.index_url = "/agency"
    mock_agency.eligibility_index_template = "eligibility/index.html"
    mocked_session_agency.return_value = mock_agency

    path = reverse(routes.ELIGIBILITY_INDEX)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == mock_agency.eligibility_index_template
    assert "form" in response.context_data
    assert isinstance(response.context_data["form"], EnrollmentFlowSelectionForm)


@pytest.mark.django_db
def test_index_get_agency_single_flow(mocker, model_TransitAgency, model_EnrollmentFlow, mocked_session_agency, client):
    # override the mocked session agency with a mock agency that has a single flow
    mock_agency = mocker.Mock(spec=model_TransitAgency)

    # mock the enrollment_flows property on the class - https://stackoverflow.com/a/55642462
    mock_manager = mocker.Mock()
    mock_manager.all.return_value = [model_EnrollmentFlow]
    type(mock_agency).enrollment_flows = mocker.PropertyMock(return_value=mock_manager)
    type(mock_agency).enrollment_flows.filter.return_value = [model_EnrollmentFlow, model_EnrollmentFlow]

    mock_agency.index_url = "/agency"
    mock_agency.eligibility_index_template = "eligibility/index.html"
    mocked_session_agency.return_value = mock_agency

    path = reverse(routes.ELIGIBILITY_INDEX)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == mock_agency.eligibility_index_template
    assert "form" in response.context_data
    assert isinstance(response.context_data["form"], EnrollmentFlowSelectionForm)


@pytest.mark.django_db
def test_index_get_without_agency(client):
    path = reverse(routes.ELIGIBILITY_INDEX)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_index_post_invalid_form(client):
    path = reverse(routes.ELIGIBILITY_INDEX)

    response = client.post(path, {"invalid": "data"})

    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_index_post_valid_form(client, model_EnrollmentFlow, mocked_session_update, mocked_analytics_module):
    path = reverse(routes.ELIGIBILITY_INDEX)

    response = client.post(path, {"flow": model_EnrollmentFlow.id})

    assert response.status_code == 302
    assert response.url == reverse(routes.ELIGIBILITY_START)
    assert mocked_session_update.call_args.kwargs["flow"] == model_EnrollmentFlow
    mocked_analytics_module.selected_flow.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request")
def test_index_calls_session_logout(client, session_logout_spy):
    path = reverse(routes.ELIGIBILITY_INDEX)

    client.get(path)

    session_logout_spy.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_flow_selection_form", "mocked_session_flow_uses_claims_verification")
def test_start_flow_uses_claims_verification_logged_in(mocker, client):
    mock_session = mocker.patch("benefits.eligibility.views.session")
    mock_session.logged_in.return_value = True

    path = reverse(routes.ELIGIBILITY_START)
    response = client.get(path)

    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_flow_selection_form", "mocked_session_flow_uses_claims_verification")
def test_start_flow_uses_claims_verification_not_logged_in(mocker, client):
    mock_session = mocker.patch("benefits.eligibility.views.session")
    mock_session.logged_in.return_value = False

    path = reverse(routes.ELIGIBILITY_START)
    response = client.get(path)

    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_session_agency", "mocked_flow_selection_form", "mocked_session_flow_does_not_use_claims_verification"
)
def test_start_flow_does_not_use_claims_verification(client):
    path = reverse(routes.ELIGIBILITY_START)
    response = client.get(path)

    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_start_without_flow(client):
    path = reverse(routes.ELIGIBILITY_START)

    response = client.get(path)
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow")
def test_confirm_get_unverified(mocker, client):
    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible", "mocked_session_flow")
def test_confirm_get_verified(client, mocked_session_update):
    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.get(path)

    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_INDEX)
    mocked_session_update.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow_uses_claims_verification", "mocked_session_oauth_token")
def test_confirm_get_oauth_verified(mocker, client, mocked_session_update, mocked_analytics_module):
    mocker.patch("benefits.eligibility.verify.eligibility_from_oauth", return_value=True)

    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.get(path)

    mocked_session_update.assert_called_once()
    mocked_analytics_module.returned_success.assert_called_once()
    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_INDEX)


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_session_agency",
    "mocked_session_flow_uses_claims_verification",
    "mocked_session_oauth_token",
    "mocked_session_update",
)
def test_confirm_get_oauth_unverified(mocker, client):
    mocker.patch("benefits.eligibility.verify.eligibility_from_oauth", return_value=[])

    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.get(path)

    assert response.status_code == 302
    assert response.url == reverse(routes.ELIGIBILITY_UNVERIFIED)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request", "model_EnrollmentFlow_with_form_class")
def test_confirm_post_invalid_form(client, invalid_form_data, mocked_analytics_module):
    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.post(path, invalid_form_data)

    mocked_analytics_module.started_eligibility.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_analytics_module", "mocked_eligibility_auth_request", "model_EnrollmentFlow_with_form_class")
def test_confirm_post_recaptcha_fail(mocker, client, invalid_form_data):
    mocker.patch("benefits.eligibility.views.recaptcha.has_error", return_value=True)
    messages = mocker.spy(benefits.eligibility.views, "messages")

    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.post(path, invalid_form_data)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM
    messages.error.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request", "model_EnrollmentFlow_with_form_class")
def test_confirm_post_valid_form_eligibility_error(mocker, client, form_data, mocked_analytics_module):
    mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=None)

    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.post(path, form_data)

    mocked_analytics_module.returned_error.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request", "model_EnrollmentFlow_with_form_class")
def test_confirm_post_valid_form_eligibility_unverified(mocker, client, form_data):
    mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=[])

    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.post(path, form_data)

    assert response.status_code == 302
    assert response.url == reverse(routes.ELIGIBILITY_UNVERIFIED)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request", "model_EnrollmentFlow_with_form_class")
def test_confirm_post_valid_form_eligibility_verified(
    mocker, client, form_data, mocked_session_eligible, mocked_session_update, mocked_analytics_module
):
    eligible = mocked_session_eligible.return_value
    mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=eligible)

    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.post(path, form_data)

    mocked_session_update.assert_called_once()
    mocked_analytics_module.returned_success.assert_called_once()
    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_INDEX)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_request_session")
def test_unverified(client, mocked_analytics_module):
    path = reverse(routes.ELIGIBILITY_UNVERIFIED)

    response = client.get(path)

    mocked_analytics_module.returned_fail.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == "eligibility/unverified.html"
