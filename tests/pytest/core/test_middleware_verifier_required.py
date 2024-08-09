from django.utils.decorators import decorator_from_middleware

import pytest

from benefits.core.middleware import FlowSessionRequired, TEMPLATE_USER_ERROR


@pytest.fixture
def decorated_view(mocked_view):
    return decorator_from_middleware(FlowSessionRequired)(mocked_view)


@pytest.mark.django_db
def test_flow_required_no_flow(app_request, mocked_view, decorated_view):
    response = decorated_view(app_request)

    mocked_view.assert_not_called()
    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow_uses_claims_verification")
def test_flow_required_flow(app_request, mocked_view, decorated_view):
    decorated_view(app_request)

    mocked_view.assert_called_once()
