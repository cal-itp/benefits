import pytest

from benefits.eligibility.analytics import EligibilityEvent


@pytest.mark.django_db
def test_EligibilityEvent_overwrites_session_eligibility_types(app_request, mocker):
    type1, type2 = "type1", "type2"
    mocker.patch("benefits.core.analytics.session.eligibility", return_value=[type1])
    mocker.patch("benefits.core.analytics.EligibilityType.get_names", return_value=[type1])

    event = EligibilityEvent(app_request, "event_type", [type2])

    assert "eligibility_types" in event.event_properties
    assert type2 in event.event_properties["eligibility_types"]
    assert type1 not in event.event_properties["eligibility_types"]
