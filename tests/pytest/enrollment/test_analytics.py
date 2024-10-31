import pytest

from benefits.enrollment.analytics import FailedAccessTokenRequestEvent, ReturnedEnrollmentEvent


@pytest.mark.django_db
def test_FailedAccessTokenRequestEvent_sets_status_code(app_request):
    event = FailedAccessTokenRequestEvent(app_request, 500)

    assert event.event_properties["status_code"] == 500


@pytest.mark.django_db
def test_ReturnedEnrollmentEvent_without_error(app_request, mocker):

    key1 = "enrollment_flows"
    key2 = "extra_claims"
    mock_flow = mocker.Mock()
    mock_flow.system_name = "flow_1"
    mocker.patch("benefits.core.session.flow", return_value=mock_flow)

    mock_claims = ["eligibility_claim", "extra_claim"]
    mocker.patch("benefits.core.session.oauth_claims", return_value=mock_claims)

    event = ReturnedEnrollmentEvent(app_request, status="success")
    assert "error_code" not in event.event_properties
    assert key1 in event.event_properties
    assert key2 in event.event_properties
