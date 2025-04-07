from cdt_identity.routes import Routes as OAuthRoutes
from django.urls import reverse

import pytest

from benefits.routes import routes
from benefits.core import session
from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.oauth.views import (
    TEMPLATE_SYSTEM_ERROR,
    system_error,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "route",
    [
        OAuthRoutes.route_login,
        OAuthRoutes.route_authorize,
        OAuthRoutes.route_cancel,
        OAuthRoutes.route_logout,
        OAuthRoutes.route_post_logout,
    ],
)
def test_url_path_no_session_flow(client, route):
    path = reverse(route)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_system_error(app_request, model_TransitAgency):
    origin = reverse(routes.ELIGIBILITY_START)
    session.update(app_request, origin=origin)

    result = system_error(app_request)

    assert result.status_code == 200
    assert result.template_name == TEMPLATE_SYSTEM_ERROR
    assert session.origin(app_request) == model_TransitAgency.index_url


@pytest.mark.django_db
def test_system_error_no_agency(app_request):
    result = system_error(app_request)

    assert result.status_code == 200
    assert result.template_name == TEMPLATE_USER_ERROR
