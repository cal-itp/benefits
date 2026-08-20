import pytest

import benefits.core.analytics
from benefits.oauth.analytics import (
    CanceledSignInEvent,
    FailureToProofEvent,
    FinishedSignInEvent,
    FinishedSignOutEvent,
    OAuthErrorEvent,
    OAuthEvent,
    StartedSignInEvent,
    StartedSignOutEvent,
    canceled_sign_in,
    error,
    failure_to_proof,
    finished_sign_in,
    finished_sign_out,
    started_sign_in,
    started_sign_out,
)


@pytest.fixture
def spy_send_event(mocker):
    return mocker.spy(benefits.core.analytics, "send_event")


@pytest.mark.django_db
def test_OAuthEvent_flow_client_name_when_uses_claims_verification(app_request, mocked_session_flow_uses_claims_verification):
    mocked_flow = mocked_session_flow_uses_claims_verification(app_request)
    mocked_flow.oauth_config.client_name = "ClientName"

    event = OAuthEvent(app_request, "event type")

    assert "claims_provider" in event.event_properties
    assert event.event_properties["claims_provider"] == mocked_flow.oauth_config.client_name


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_does_not_use_claims_verification")
def test_OAuthEvent_flow_no_client_name_when_does_not_use_claims_verification(app_request):
    event = OAuthEvent(app_request, "event type")

    assert "claims_provider" not in event.event_properties


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_OAuthErrorEvent(app_request):
    event_default = OAuthErrorEvent(app_request, "the message", "the operation")

    assert event_default.event_type == "oauth error"
    assert event_default.event_properties["message"] == "the message"
    assert event_default.event_properties["operation"] == "the operation"


@pytest.mark.django_db
def test_FinishedSignInEvent_with_error(app_request):
    event = FinishedSignInEvent(app_request, error=10)
    assert event.event_properties["error_code"] == 10


@pytest.mark.django_db
def test_FinishedSignInEvent_without_error(app_request):
    event = FinishedSignInEvent(app_request)
    assert "error_code" not in event.event_properties


@pytest.mark.django_db
def test_error(app_request, spy_send_event):
    error(app_request, "the message", "the operation")

    # event should have been sent
    spy_send_event.assert_called_once()
    # the first arg of the first (and only) call
    call_arg = spy_send_event.call_args[0][0]
    assert isinstance(call_arg, OAuthErrorEvent)
    assert call_arg.event_type == "oauth error"
    assert call_arg.event_properties["message"] == "the message"
    assert call_arg.event_properties["operation"] == "the operation"


@pytest.mark.django_db
def test_started_sign_in(app_request, spy_send_event):
    started_sign_in(app_request)

    # event should have been sent
    spy_send_event.assert_called_once()
    # the first arg of the first (and only) call
    call_arg = spy_send_event.call_args[0][0]
    assert isinstance(call_arg, StartedSignInEvent)
    assert call_arg.event_type == "started sign in"


@pytest.mark.django_db
def test_canceled_sign_in(app_request, spy_send_event):
    canceled_sign_in(app_request)

    # event should have been sent
    spy_send_event.assert_called_once()
    # the first arg of the first (and only) call
    call_arg = spy_send_event.call_args[0][0]
    assert isinstance(call_arg, CanceledSignInEvent)
    assert call_arg.event_type == "canceled sign in"


@pytest.mark.django_db
def test_finished_sign_in(app_request, spy_send_event):
    finished_sign_in(app_request)

    # event should have been sent
    spy_send_event.assert_called_once()
    # the first arg of the first (and only) call
    call_arg = spy_send_event.call_args[0][0]
    assert isinstance(call_arg, FinishedSignInEvent)
    assert call_arg.event_type == "finished sign in"


@pytest.mark.django_db
def test_started_sign_out(app_request, spy_send_event):
    started_sign_out(app_request)

    # event should have been sent
    spy_send_event.assert_called_once()
    # the first arg of the first (and only) call
    call_arg = spy_send_event.call_args[0][0]
    assert isinstance(call_arg, StartedSignOutEvent)
    assert call_arg.event_type == "started sign out"


@pytest.mark.django_db
def test_finished_sign_out(app_request, spy_send_event):
    finished_sign_out(app_request)

    # event should have been sent
    spy_send_event.assert_called_once()
    # the first arg of the first (and only) call
    call_arg = spy_send_event.call_args[0][0]
    assert isinstance(call_arg, FinishedSignOutEvent)
    assert call_arg.event_type == "finished sign out"


@pytest.mark.django_db
def test_failure_to_proof(app_request, spy_send_event):
    failure_to_proof(app_request)

    # event should have been sent
    spy_send_event.assert_called_once()
    # the first arg of the first (and only) call
    call_arg = spy_send_event.call_args[0][0]
    assert isinstance(call_arg, FailureToProofEvent)
    assert call_arg.event_type == "failure to proof"
