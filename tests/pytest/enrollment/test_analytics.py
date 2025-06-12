import pytest

from cdt_identity.claims import ClaimsResult
from benefits.enrollment.analytics import FailedPretokenizationRequestEvent, ReturnedEnrollmentEvent


@pytest.mark.django_db
def test_FailedAccessTokenRequestEvent_sets_status_code(app_request):
    event = FailedPretokenizationRequestEvent(app_request, 500)

    assert event.event_properties["status_code"] == 500


@pytest.mark.django_db
def test_ReturnedEnrollmentEvent_without_error(app_request, mocker):

    key1 = "enrollment_flows"
    key2 = "extra_claims"
    mock_flow = mocker.Mock()
    mock_flow.system_name = "flow_1"
    mocker.patch("benefits.core.session.flow", return_value=mock_flow)

    mock_verified = {"eligibility_claim": "medicare", "extra_claim": "disabled"}
    mocker.patch("benefits.core.session.OAuthSession.claims_result", return_value=ClaimsResult(verified=mock_verified))

    event = ReturnedEnrollmentEvent(app_request, status="success")
    assert "error_code" not in event.event_properties
    assert key1 in event.event_properties
    assert key2 in event.event_properties
