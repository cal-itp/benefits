import pytest
from django.utils.decorators import decorator_from_middleware

from benefits.core.middleware import SessionCache


@pytest.fixture
def decorated_view(mocked_view):
    return decorator_from_middleware(SessionCache)(mocked_view)


@pytest.mark.django_db
def test_session_cache_initializes_properties(app_request, mocked_view, decorated_view):
    decorated_view(app_request)

    # Assert the middleware allowed the request to proceed to the view
    mocked_view.assert_called_once()

    # Assert the cache properties were properly initialized to None
    assert hasattr(app_request, "_cached_agency")
    assert app_request._cached_agency is None

    assert hasattr(app_request, "_cached_flow")
    assert app_request._cached_flow is None
