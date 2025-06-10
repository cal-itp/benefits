import pytest
from django.urls import reverse

from benefits.routes import routes
import benefits.enrollment.views
import benefits.enrollment.enrollment
from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.enrollment.views import TEMPLATE_RETRY, system_error


@pytest.fixture
def card_tokenize_form_data():
    return {"card_token": "tokenized_card"}


@pytest.fixture
def invalid_form_data():
    return {"invalid": "data"}


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.enrollment.views)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.enrollment.enrollment, "sentry_sdk")


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_index_eligible_get_littlepay(client):
    path = reverse(routes.ENROLLMENT_INDEX)
    response = client.get(path)

    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_LITTLEPAY_INDEX)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow", "mocked_session_eligible")
def test_index_eligible_get_switchio(client, mocked_session_agency, model_SwitchioConfig):
    mock_agency = mocked_session_agency(None)
    mock_agency.littlepay_config = None
    mock_agency.switchio_config = model_SwitchioConfig
    mock_agency.save()

    path = reverse(routes.ENROLLMENT_INDEX)
    response = client.get(path)

    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_SWITCHIO_INDEX)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow", "mocked_session_eligible")
def test_system_error(
    mocker,
    app_request,
    mocked_session_agency,
):
    mock_session = mocker.patch("benefits.enrollment.views.session")
    mock_session.agency.return_value = mocked_session_agency.return_value

    system_error(app_request)

    assert {"origin": mocked_session_agency.return_value.index_url} in mock_session.update.call_args


@pytest.mark.django_db
def test_index_ineligible(client):
    path = reverse(routes.ENROLLMENT_INDEX)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
def test_reenrollment_error_ineligible(client):
    path = reverse(routes.ENROLLMENT_REENROLLMENT_ERROR)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_reenrollment_error_eligibility_no_error_template(client):
    path = reverse(routes.ENROLLMENT_REENROLLMENT_ERROR)

    with pytest.raises(Exception, match="Re-enrollment error with null template"):
        client.get(path)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow")
def test_reenrollment_error(client, model_EnrollmentFlow_supports_expiration, mocked_session_eligible):
    mocked_session_eligible.return_value = model_EnrollmentFlow_supports_expiration

    path = reverse(routes.ENROLLMENT_REENROLLMENT_ERROR)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == model_EnrollmentFlow_supports_expiration.reenrollment_error_template


@pytest.mark.django_db
def test_retry_ineligible(client):
    path = reverse(routes.ENROLLMENT_RETRY)

    response = client.post(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_retry_get(client, mocked_analytics_module):
    path = reverse(routes.ENROLLMENT_RETRY)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_RETRY
    mocked_analytics_module.returned_retry.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible")
def test_retry_valid_form(client, mocked_analytics_module):
    path = reverse(routes.ENROLLMENT_RETRY)
    response = client.post(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_RETRY
    mocked_analytics_module.returned_retry.assert_called_once()


@pytest.mark.django_db
def test_success_no_flow(client):
    path = reverse(routes.ENROLLMENT_SUCCESS)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification", "mocked_session_eligible")
def test_success_authentication_logged_in(mocker, client, model_TransitAgency, model_EnrollmentFlow_supports_sign_out):
    mock_session = mocker.patch("benefits.enrollment.views.session")
    mock_session.logged_in.return_value = True
    mock_session.agency.return_value = model_TransitAgency
    mock_session.flow.return_value = model_EnrollmentFlow_supports_sign_out

    path = reverse(routes.ENROLLMENT_SUCCESS)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == "enrollment/success.html"
    assert {"origin": reverse(routes.LOGGED_OUT)} in mock_session.update.call_args


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification", "mocked_session_eligible")
def test_success_authentication_not_logged_in(mocker, client, model_TransitAgency, model_EnrollmentFlow):
    mock_session = mocker.patch("benefits.enrollment.views.session")
    mock_session.logged_in.return_value = False
    mock_session.agency.return_value = model_TransitAgency
    mock_session.flow.return_value = model_EnrollmentFlow

    path = reverse(routes.ENROLLMENT_SUCCESS)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == "enrollment/success.html"


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "mocked_session_agency", "mocked_session_eligible", "mocked_session_flow_does_not_use_claims_verification"
)
def test_success_no_authentication(client):
    path = reverse(routes.ENROLLMENT_SUCCESS)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == "enrollment/success.html"
