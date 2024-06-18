import pytest

from benefits.enrollment.analytics import FailedAccessTokenRequestEvent


@pytest.mark.django_db
def test_FailedAccessTokenRequestEvent_sets_status_code(app_request):
    event = FailedAccessTokenRequestEvent(app_request, 500)

    assert event.event_properties["status_code"] == 500
