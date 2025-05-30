import json
import pytest

from benefits.enrollment_switchio.views import GatewayUrlView, IndexView


class TestIndexView:
    @pytest.fixture
    def view(self, app_request):
        """Fixture to create an instance of IndexView."""
        v = IndexView()
        v.setup(app_request)

        return v

    @pytest.mark.django_db
    @pytest.mark.usefixtures("mocked_session_flow")
    def test_get_context_data(self, view):

        context = view.get_context_data()

        assert "cta_button" in context
        assert "enrollment_method" in context
        assert "headline" in context
        assert "next_step" in context
        assert "partner_post_link" in context
        assert "alert_include" in context
        assert "transit_processor" in context.keys()
        transit_processor_context = context["transit_processor"]
        assert "name" in transit_processor_context
        assert "website" in transit_processor_context


class TestGatewayUrlView:
    @pytest.fixture
    def view(self, app_request):
        """Fixture to create an instance of GatewayUrlView."""
        v = GatewayUrlView()
        v.setup(app_request)

        return v

    @pytest.mark.django_db
    def test_get_gateway_url(self, view, app_request):

        response = view.get(app_request)

        assert response.status_code == 200
        assert json.loads(response.content) == {"gateway_url": "https://server/gateway/uuid"}
