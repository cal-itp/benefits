import pytest
from cdt_identity.routes import Routes as OAuthRoutes
from django.urls import reverse

from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.oauth.views import SystemErrorView


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
class TestSystemErrorView:
    @pytest.fixture
    def view(self, app_request):
        v = SystemErrorView()
        v.setup(app_request)
        return v

    def test_view(self, view):
        assert view.template_name == "oauth/system_error.html"

    @pytest.mark.usefixtures("mocked_session_agency")
    def test_get(self, mocker, view, app_request, model_TransitAgency, mocked_session_update):
        # spy on the call to get() but call dispatch() like a real request
        spy = mocker.spy(view, "get")
        response = view.dispatch(app_request)

        spy.assert_called_once()
        assert response.status_code == 200
        mocked_session_update.assert_called_once_with(app_request, origin=model_TransitAgency.index_url)
