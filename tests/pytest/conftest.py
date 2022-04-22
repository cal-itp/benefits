from django.contrib.sessions.middleware import SessionMiddleware

import pytest


@pytest.fixture(scope="session")
def django_db_setup():
    # use existing database since it's read-only
    pass


@pytest.fixture
def session_request(request, rf):
    """
    Fixture creates a new Django request object and initializes its session.

    Optionally use @pytest.mark.request_path(path: str) to customize the request's path.
    """

    # see if a request_path was provided via marker
    marker = request.node.get_closest_marker("request_path")
    if marker is None:
        request_path = "/"
    else:
        request_path = marker.args[0]

    # create a request for the path, initialize session
    session_request = rf.get(request_path)
    initialize_session(session_request)

    return session_request


def initialize_session(request):
    """Helper initializes a Django request object's session."""

    # https://stackoverflow.com/a/55530933/358804
    middleware = SessionMiddleware(lambda x: x)
    middleware.process_request(request)
    request.session.save()
