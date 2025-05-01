from django.views import View

import pytest

from benefits.core.middleware import TEMPLATE_USER_ERROR
from benefits.core.mixins import AgencySessionRequiredMixin, FlowSessionRequiredMixin


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
