from django.contrib.sessions.middleware import SessionMiddleware
from django.middleware.locale import LocaleMiddleware
from django.utils.decorators import decorator_from_middleware
from django.views import i18n

import benefits.core.analytics
from benefits.core.analytics import ChangedLanguageEvent as Analytics_ChangedLanguageEvent
from benefits.core.middleware import ChangedLanguageEvent as Middleware_ChangedLanguageEvent

import pytest


@pytest.fixture
def request_nolanguage(rf):
    """
    Fixture creates and initializes a new Django POST request without a language parameter in the body
    """
    # create a request for the path, initialize
    post_request = rf.post("/some/path")

    # https://stackoverflow.com/a/55530933/358804
    middleware = [SessionMiddleware(lambda x: x), LocaleMiddleware(lambda x: x)]
    for m in middleware:
        m.process_request(post_request)

    post_request.session.save()

    return post_request


@pytest.fixture
def request_withlanguage(rf):
    """
    Fixture creates and initializes a new Django POST request with a language parameter in the body
    """
    # create a request for the path with a language parameter
    post_request = rf.post("/some/path", {"language": "es"})

    # https://stackoverflow.com/a/55530933/358804
    middleware = [SessionMiddleware(lambda x: x), LocaleMiddleware(lambda x: x)]
    for m in middleware:
        m.process_request(post_request)

    post_request.session.save()

    return post_request


@pytest.fixture
def decorated_view_not_i18n(mocked_view):
    return decorator_from_middleware(Middleware_ChangedLanguageEvent)(mocked_view)


@pytest.fixture
def decorated_view_i18n():
    return decorator_from_middleware(Middleware_ChangedLanguageEvent)(i18n.set_language)


@pytest.fixture
def spy_send_event(mocker):
    return mocker.spy(benefits.core.analytics, "send_event")


@pytest.mark.django_db
def test_changed_language_wrong_view_func(request_withlanguage, decorated_view_not_i18n, spy_send_event):
    # we don't need the response
    decorated_view_not_i18n(request_withlanguage)

    # event should not have been sent
    spy_send_event.assert_not_called()


@pytest.mark.django_db
def test_changed_language_no_language(request_nolanguage, decorated_view_i18n, spy_send_event):
    # we don't need the response
    decorated_view_i18n(request_nolanguage)

    # event should not have been sent
    spy_send_event.assert_not_called()


@pytest.mark.django_db
def test_changed_language_with_language(request_withlanguage, decorated_view_i18n, spy_send_event):
    # we don't need the response
    decorated_view_i18n(request_withlanguage)

    # event should have been sent
    spy_send_event.assert_called_once()
    # the first arg of the first (and only) call
    call_arg = spy_send_event.call_args[0][0]
    assert isinstance(call_arg, Analytics_ChangedLanguageEvent)
