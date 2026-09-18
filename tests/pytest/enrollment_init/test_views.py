import pytest

import benefits.enrollment_littlepay.views
from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.core.models.transit import CardSchemes
from benefits.enrollment_init.views import IndexView


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.enrollment_littlepay.views)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.enrollment_littlepay.views, "sentry_sdk")


@pytest.mark.django_db
class TestIndexView:
    @pytest.fixture
    def view(self, app_request, model_TransitAgency, model_InitConfig, model_EnrollmentFlow):
        """Fixture to create an instance of IndexView."""
        v = IndexView()
        v.setup(app_request)
        v.agency = model_InitConfig
        v.agency.supported_card_schemes = [CardSchemes.DISCOVER, CardSchemes.AMEX]
        v.flow = model_EnrollmentFlow

        return v

    def test_get_context_data(self, view):
        context = view.get_context_data()

        assert "headline" in context
        assert "next_step" in context
        assert "partner_post_link" in context
        assert "alert_include" in context

        assert "transit_processor" in context
        transit_processor_context = context["transit_processor"]
        assert "name" in transit_processor_context
        assert "website" in transit_processor_context

    @pytest.mark.usefixtures("mocked_session_eligible", "mocked_session_agency", "mocked_session_flow", "model_InitConfig")
    def test_index_view(self, app_request):
        index_view = IndexView.as_view()
        response = index_view(app_request)

        assert response.status_code == 200
        assert response.template_name == ["enrollment_init/index.html"]

    @pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow")
    def test_index_view_not_eligible(self, mocker, app_request):
        mocker.patch("benefits.core.session.eligible", return_value=False)

        index_view = IndexView.as_view()
        response = index_view(app_request)

        assert response.status_code == 200
        assert response.template_name == TEMPLATE_USER_ERROR
