import pytest

from cdt_identity.claims import ClaimsResult
import benefits.core.analytics
from benefits.enrollment.analytics import FailedPretokenizationRequestEvent, ReturnedEnrollmentEvent, returned_success


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


@pytest.mark.django_db
@pytest.mark.usefixtures("model_LittlepayGroup")
def test_returned_success_sends_event_with_optional_data(app_request, mocker, model_EnrollmentFlow_with_scope_and_claim):
    keys = ["enrollment_group", "extra_claims", "card_scheme", "card_category"]
    spy_send_event = mocker.spy(benefits.core.analytics, "send_event")
    returned_success(
        app_request, model_EnrollmentFlow_with_scope_and_claim.group_id, card_scheme="visa", card_category="debit"
    )

    # event should have been sent
    spy_send_event.assert_called_once()
    # the first arg of the first (and only) call
    call_arg = spy_send_event.call_args[0][0]
    assert isinstance(call_arg, ReturnedEnrollmentEvent)
    for key in keys:
        assert key in call_arg.event_properties
