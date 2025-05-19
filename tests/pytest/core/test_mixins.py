from django.views import View

import pytest

from benefits.core import recaptcha
from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.core.mixins import (
    AgencySessionRequiredMixin,
    EligibleSessionRequiredMixin,
    FlowSessionRequiredMixin,
    RecaptchaEnabledMixin,
)


class TestAgencySessionRequiredMixin:
    class SampleView(AgencySessionRequiredMixin, View):
        pass

    @pytest.fixture
    def view(self, app_request):
        v = self.SampleView()
        v.setup(app_request)
        return v

    def test_dispatch_without_active_agency(self, view, app_request, mocker):
        mock_session = mocker.patch("benefits.core.mixins.session")
        mock_session.active_agency.return_value = False

        response = view.dispatch(app_request)

        assert not hasattr(view, "agency")
        assert response.status_code == 200
        assert response.template_name == TEMPLATE_USER_ERROR

    def test_dispatch_with_active_agency(self, view, app_request, mocker):
        mock_session = mocker.patch("benefits.core.mixins.session")
        mock_session.active_agency.return_value = True
        mock_session.agency.return_value = {"agency": "123"}

        view.dispatch(app_request)

        assert view.agency == {"agency": "123"}


class TestEligibleSessionRequiredMixin:
    class SampleView(EligibleSessionRequiredMixin, View):
        def get(self, request, *args, **kwargs):
            return "Success"

    @pytest.fixture
    def view(self, app_request):
        v = self.SampleView()
        v.setup(app_request)
        return v

    def test_dispatch_without_eligibility(self, view, app_request, mocker):
        mock_session = mocker.patch("benefits.core.mixins.session")
        mock_session.eligible.return_value = False

        response = view.dispatch(app_request)

        assert response.status_code == 200
        assert response.template_name == TEMPLATE_USER_ERROR

    def test_dispatch_with_eligibility(self, view, app_request, mocker):
        mock_session = mocker.patch("benefits.core.mixins.session")
        mock_session.eligible.return_value = True

        response = view.dispatch(app_request)

        assert response == "Success"


class TestFlowSessionRequiredMixin:
    class SampleView(FlowSessionRequiredMixin, View):
        pass

    @pytest.fixture
    def view(self, app_request):
        v = self.SampleView()
        v.setup(app_request)
        return v

    def test_dispatch_without_flow(self, view, app_request, mocker):
        mock_session = mocker.patch("benefits.core.mixins.session")
        mock_session.flow.return_value = False

        response = view.dispatch(app_request)

        assert not hasattr(view, "flow")
        assert response.status_code == 200
        assert response.template_name == TEMPLATE_USER_ERROR

    def test_dispatch_with_flow(self, view, app_request, mocker):
        mock_session = mocker.patch("benefits.core.mixins.session")
        mock_session.flow.return_value = {"flow": "123"}

        view.dispatch(app_request)

        assert view.flow == {"flow": "123"}


class TestRecaptchaEnabledMixin:
    class SampleView(RecaptchaEnabledMixin, View):
        pass

    @pytest.fixture
    def view(self, app_request):
        v = self.SampleView()
        v.setup(app_request)
        return v

    def test_dispatch_with_recaptcha_enabled(self, view, app_request, settings):
        settings.RECAPTCHA_SITE_KEY = "recaptcha_site_key"
        settings.RECAPTCHA_API_KEY_URL = "recaptcha_api_key_url"
        settings.RECAPTCHA_ENABLED = True

        view.dispatch(app_request)

        assert app_request.recaptcha["data_field"] == recaptcha.DATA_FIELD
        assert app_request.recaptcha["script_api"] == settings.RECAPTCHA_API_KEY_URL
        assert app_request.recaptcha["site_key"] == settings.RECAPTCHA_SITE_KEY

    def test_dispatch_without_recaptcha_enabled(self, view, app_request, settings):
        settings.RECAPTCHA_ENABLED = False

        view.dispatch(app_request)

        assert not hasattr(app_request, "recaptcha")
