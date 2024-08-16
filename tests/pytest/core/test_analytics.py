import pytest

import benefits.core.analytics
from benefits.core.analytics import Event, ViewedPageEvent
from django.contrib.sessions.middleware import SessionMiddleware
from django.middleware.locale import LocaleMiddleware


@pytest.fixture
def app_request_utm(rf):
    """
    Fixture creates and initializes a new Django request object similar to a real application request with UTM codes.
    """
    # create a request for the path with UTM codes, initialize
    app_request = rf.get(
        "/some/arbitrary/path?utm_campaign=campaign&utm_source=source&utm_medium=medium&utm_content=content&utm_id=id"
    )

    # https://stackoverflow.com/a/55530933/358804
    middleware = [SessionMiddleware(lambda x: x), LocaleMiddleware(lambda x: x)]
    for m in middleware:
        m.process_request(app_request)

    app_request.session.save()
    benefits.core.analytics.session.reset(app_request)

    return app_request


@pytest.fixture
def utm_code_data():
    return {
        "utm_campaign": "campaign",
        "utm_source": "source",
        "utm_medium": "medium",
        "utm_content": "content",
        "utm_id": "id",
    }


@pytest.mark.django_db
@pytest.mark.parametrize("event_type", ["EVENT_TYPE", "eVeNt TyPe", "event-type"])
def test_Event_event_type_lowercase(app_request, event_type):
    expected = str(event_type).lower()
    event = Event(app_request, event_type)

    assert event.event_type == expected


@pytest.mark.django_db
def test_Event_reads_session(app_request, mocker):
    session_spy = mocker.spy(benefits.core.analytics, "session")

    Event(app_request, "event_type")

    session_spy.agency.assert_called_once_with(app_request)
    session_spy.did.assert_called_once_with(app_request)
    session_spy.language.assert_called_once_with(app_request)
    session_spy.start.assert_called_once_with(app_request)
    session_spy.uid.assert_called_once_with(app_request)
    session_spy.flow.assert_called_once_with(app_request)


@pytest.mark.django_db
def test_Event_sets_default_event_properties(app_request, mocker):
    update_spy = mocker.spy(benefits.core.analytics.Event, "update_event_properties")

    Event(app_request, "event_type")

    assert "path" in update_spy.call_args.kwargs
    assert "transit_agency" in update_spy.call_args.kwargs
    assert "eligibility_types" in update_spy.call_args.kwargs
    assert "eligibility_verifier" in update_spy.call_args.kwargs


@pytest.mark.django_db
def test_Event_sets_default_user_properties(app_request, mocker):
    update_spy = mocker.spy(benefits.core.analytics.Event, "update_user_properties")

    Event(app_request, "event_type")

    assert "referrer" in update_spy.call_args.kwargs
    assert "referring_domain" in update_spy.call_args.kwargs
    assert "user_agent" in update_spy.call_args.kwargs
    assert "transit_agency" in update_spy.call_args.kwargs
    assert "eligibility_types" in update_spy.call_args.kwargs
    assert "eligibility_verifier" in update_spy.call_args.kwargs


@pytest.mark.django_db
def test_Event_update_event_properties(app_request):
    key, value = "key", "value"
    event = Event(app_request, "event_type")

    assert len(event.event_properties) > 0
    assert key not in event.event_properties

    event.update_event_properties(**{key: value})

    assert key in event.event_properties
    assert event.event_properties[key] == value


@pytest.mark.django_db
def test_Event_update_user_properties(app_request):
    key, value = "key", "value"
    event = Event(app_request, "event_type")

    assert len(event.user_properties) > 0
    assert key not in event.user_properties

    event.update_user_properties(**{key: value})

    assert key in event.user_properties
    assert event.user_properties[key] == value


@pytest.mark.django_db
def test_ViewedPageEvent_with_UTM(app_request_utm, utm_code_data):
    event = ViewedPageEvent(app_request_utm)

    for key, value in utm_code_data.items():
        assert event.event_properties[key] == value
        assert event.user_properties[key] == value


@pytest.mark.django_db
def test_ViewedPageEvent_without_UTM(app_request, utm_code_data):
    event = ViewedPageEvent(app_request)

    for key in utm_code_data:
        assert event.event_properties[key] is None
        assert event.user_properties[key] is None
