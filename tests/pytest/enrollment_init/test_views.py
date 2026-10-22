import json

import pytest

import benefits.enrollment_init.views
from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.core.models.transit import CardSchemes
from benefits.enrollment_init.views import IndexView, RegisterView


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(benefits.enrollment_init.views)


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(benefits.enrollment_init.views, "sentry_sdk")


@pytest.mark.django_db
class TestIndexView:
    @pytest.fixture
    def view(self, app_request, model_TransitAgency, model_EnrollmentFlow):
        """Fixture to create an instance of IndexView."""
        v = IndexView()
        v.setup(app_request)
        v.agency = model_TransitAgency
        v.agency.supported_card_schemes = [CardSchemes.DISCOVER, CardSchemes.AMEX]
        v.flow = model_EnrollmentFlow

        return v

    def test_get_context_data(self, view):
        context = view.get_context_data()

        assert "cta_button" in context

        assert "transit_processor" in context
        transit_processor_context = context["transit_processor"]
        assert "name" in transit_processor_context
        assert "website" in transit_processor_context

    @pytest.mark.usefixtures("mocked_session_eligible")
    def test_get(self, view, app_request):
        response = view.get(app_request)

        assert response.status_code == 200
        assert response.template_name == ["enrollment_init/index.html"]

    def test_get_not_eligible(self, view, app_request, mocker):
        mocker.patch("benefits.core.session.eligible", return_value=False)
        response = view.dispatch(app_request)

        assert response.status_code == 200
        assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
class TestRegisterView:
    @pytest.fixture
    def view(self, app_request, model_TransitAgency, model_InitConfig, model_EnrollmentFlow):
        """Fixture to create an instance of RegisterView."""
        v = RegisterView()
        v.setup(app_request)
        v.agency = model_TransitAgency

        v.agency.supported_card_schemes = [CardSchemes.VISA, CardSchemes.MASTERCARD, CardSchemes.DISCOVER]
        v.flow = model_EnrollmentFlow

        return v

    def test_get_context_data(self, view):
        context = view.get_context_data()

        assert "collect_js_api_key" in context
        assert "form_success" in context
        assert "form_system_error" in context
        assert "success_url" in context
        assert "card_schemes" in context

        parsed_card_types = json.loads(context["card_schemes"])
        assert parsed_card_types == [CardSchemes.VISA, CardSchemes.MASTERCARD, CardSchemes.DISCOVER]

    def test_form_valid(self, view):
        form = view.form_class(data=dict(card_token="abc123"))

        assert form.is_valid()
        view.form_valid(form)
