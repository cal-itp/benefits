from django.contrib.sessions.middleware import SessionMiddleware
from django.middleware.locale import LocaleMiddleware

import pytest

from benefits.core import session


@pytest.fixture(scope="session")
def django_db_setup():
    # use existing database since it's read-only
    pass


@pytest.fixture
def app_request(request, rf):
    """
    Fixture creates and initializes a new Django request object similar to a real application request.

    Optionally use @pytest.mark.request_path(path: str) to customize the request's path.
    """

    # see if a request_path was provided via marker
    marker = request.node.get_closest_marker("request_path")
    request_path = marker.args[0] if marker else "/some/arbitrary/path"

    # create a request for the path, initialize
    app_request = rf.get(request_path)
    initialize_request(app_request)

    return app_request


def initialize_request(request):
    """Helper initializes a Django request object with session and language information."""

    # https://stackoverflow.com/a/55530933/358804
    middleware = [SessionMiddleware(lambda x: x), LocaleMiddleware(lambda x: x)]

    for m in middleware:
        m.process_request(request)

    request.session.save()

    session.reset(request)
