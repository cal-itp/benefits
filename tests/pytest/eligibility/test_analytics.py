import pytest

from benefits.eligibility.analytics import EligibilityEvent


@pytest.mark.django_db
def test_EligibilityEvent_overwrites_enrollment_flows(app_request, mocker, model_EnrollmentFlow):
    key, type1, type2 = "enrollment_flows", "type1", "type2"
    model_EnrollmentFlow.system_name = type1
    mocker.patch("benefits.core.analytics.session.flow", return_value=model_EnrollmentFlow)

    event = EligibilityEvent(app_request, "event_type", type2)

    # event_properties should have been overwritten
    assert key in event.event_properties
    assert type2 in event.event_properties[key]
    assert type1 not in event.event_properties[key]

    # user_properties should have been overwritten
    assert key in event.user_properties
    assert type2 in event.user_properties[key]
    assert type1 not in event.user_properties[key]
