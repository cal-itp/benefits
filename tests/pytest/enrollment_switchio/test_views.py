import json
import pytest

from benefits.enrollment_switchio.api import Registration
import benefits.enrollment_switchio.views
from benefits.enrollment_switchio.views import GatewayUrlView, IndexView


@pytest.fixture
def mocked_api_base_url(mocker):
    return mocker.patch(
        "benefits.enrollment_switchio.models.get_secret_by_name", return_value="https://example.com/backend-api"
    )


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
    @pytest.mark.usefixtures("mocked_api_base_url", "mocked_session_agency", "mocked_session_eligible")
    def test_get_gateway_url(self, view, app_request, mocker, model_TransitAgency, model_SwitchioConfig):
        model_TransitAgency.switchio_config = model_SwitchioConfig
        gateway_url = "https://example.com/cst/?regId=1234"
        mocker.patch(
            "benefits.enrollment_switchio.views.Client.request_registration",
            return_value=Registration(regId="1234", gtwUrl=gateway_url),
        )
        session_spy = mocker.spy(benefits.enrollment_switchio.views, "Session")

        # need to call `dispatch` here so that variables that the mixins assign (e.g. self.agency) are available to the view
        response = view.dispatch(app_request)

        assert response.status_code == 200
        assert json.loads(response.content) == {"gateway_url": gateway_url}
        session_spy.assert_called_once_with(request=app_request, registration_id="1234")
