from django.urls import reverse
import pytest
from requests import HTTPError

from benefits.core import models
from benefits.routes import routes
import benefits.enrollment.enrollment
from benefits.enrollment.enrollment import Status, handle_enrollment_results


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.enrollment.enrollment)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.enrollment.enrollment, "sentry_sdk")


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible", "model_LittlepayGroup")
def test_handle_enrollment_results_success_claims(
    mocker,
    app_request,
    mocked_session_oauth_extra_claims,
    model_TransitAgency,
    model_EnrollmentFlow_with_scope_and_claim,
    mocked_analytics_module,
):
    mocked_session_oauth_extra_claims.return_value = ["claim_1", "claim_2"]
    spy = mocker.spy(benefits.enrollment.enrollment.models.EnrollmentEvent.objects, "create")

    response = handle_enrollment_results(app_request, Status.SUCCESS)

    spy.assert_called_once_with(
        transit_agency=model_TransitAgency,
        enrollment_flow=model_EnrollmentFlow_with_scope_and_claim,
        enrollment_method=models.EnrollmentMethods.DIGITAL,
        verified_by=model_EnrollmentFlow_with_scope_and_claim.oauth_config.client_name,
        expiration_datetime=None,
        extra_claims="claim_1, claim_2",
    )

    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_SUCCESS)
    mocked_analytics_module.returned_success.assert_called_once()
    analytics_kwargs = mocked_analytics_module.returned_success.call_args.kwargs
    assert analytics_kwargs["enrollment_group"] == model_EnrollmentFlow_with_scope_and_claim.group_id
    assert analytics_kwargs["enrollment_method"] == models.EnrollmentMethods.DIGITAL


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible", "model_LittlepayGroup")
def test_handle_enrollment_results_success_eligibility_api(
    mocker,
    app_request,
    mocked_session_oauth_extra_claims,
    model_TransitAgency,
    model_EnrollmentFlow_with_eligibility_api,
    mocked_analytics_module,
):
    mocked_session_oauth_extra_claims.return_value = ["claim_1", "claim_2"]
    spy = mocker.spy(benefits.enrollment.enrollment.models.EnrollmentEvent.objects, "create")

    response = handle_enrollment_results(app_request, Status.SUCCESS)

    spy.assert_called_once_with(
        transit_agency=model_TransitAgency,
        enrollment_flow=model_EnrollmentFlow_with_eligibility_api,
        enrollment_method=models.EnrollmentMethods.DIGITAL,
        verified_by=model_EnrollmentFlow_with_eligibility_api.eligibility_api_url,
        expiration_datetime=None,
        extra_claims="claim_1, claim_2",
    )

    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_SUCCESS)
    mocked_analytics_module.returned_success.assert_called_once()
    analytics_kwargs = mocked_analytics_module.returned_success.call_args.kwargs
    assert analytics_kwargs["enrollment_group"] == model_EnrollmentFlow_with_eligibility_api.group_id
    assert analytics_kwargs["enrollment_method"] == models.EnrollmentMethods.DIGITAL


@pytest.mark.parametrize("status_code", [500, 501, 502, 503, 504])
def test_handle_enrollment_results_system_error(
    mocker, app_request, status_code, mocked_analytics_module, mocked_sentry_sdk_module
):
    mock_error = {"message": "Mock error message"}
    mock_error_response = mocker.Mock(status_code=status_code, **mock_error)
    mock_error_response.json.return_value = mock_error

    mock_exception = HTTPError(response=mock_error_response)

    response = handle_enrollment_results(app_request, Status.SYSTEM_ERROR, mock_exception)

    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_SYSTEM_ERROR)
    mocked_analytics_module.returned_error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


def test_handle_enrollment_results_exception(app_request, mocked_analytics_module):
    with pytest.raises(Exception, match=r"some exception"):
        handle_enrollment_results(app_request, Status.EXCEPTION, Exception("some exception"))

        mocked_analytics_module.returned_error.assert_called_once()


def test_handle_enrollment_results_reenrollment_error(app_request, mocked_analytics_module):
    response = handle_enrollment_results(app_request, Status.REENROLLMENT_ERROR)

    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_REENROLLMENT_ERROR)
    mocked_analytics_module.returned_error.assert_called_once()
