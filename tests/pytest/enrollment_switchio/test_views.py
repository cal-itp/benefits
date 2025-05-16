import json
import pytest

from benefits.enrollment_switchio.views import GatewayUrlView, IndexView


class TestIndexView:
    @pytest.mark.django_db
    def test_get_context_data(self, app_request, mocker, model_EnrollmentFlow):
        view = IndexView()
        view.setup(app_request)
        mocker.patch("benefits.core.session.flow", return_value=model_EnrollmentFlow)
        context = view.get_context_data()

        assert "cta_button" in context
        assert "enrollment_method" in context
        assert "headline" in context
        assert "next_step" in context
        assert "partner_post_link" in context
        assert "alert_include" in context
        assert "transit_processor" in context


class TestGatewayUrlView:
    @pytest.mark.django_db
    def test_get_gateway_url(self, app_request):

        response = GatewayUrlView.as_view()(app_request)

        assert response.status_code == 200
        assert json.loads(response.content) == {"gateway_url": "https://server/gateway/uuid"}
