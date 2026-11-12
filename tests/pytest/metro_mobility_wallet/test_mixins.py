import pytest
from django.urls import reverse
from django.views import View

from benefits.metro_mobility_wallet.mixins import TermsAcceptanceRequiredMixin


class TestTermsAcceptanceRequiredMixin:
    class SampleView(TermsAcceptanceRequiredMixin, View):
        def get(self, request, *args, **kwargs):
            return "Success"

    @pytest.fixture
    def view(self, app_request):
        v = self.SampleView()
        v.setup(app_request)
        return v

    def test_dispatch_without_accepted_terms(self, view, app_request, mocker):
        mock_session = mocker.patch("benefits.metro_mobility_wallet.mixins.Session")
        mock_session.return_value.accepted_terms = False

        response = view.dispatch(app_request)

        assert response.status_code == 302
        assert response.url == reverse("metro_mobility_wallet:terms")

    def test_dispatch_with_accepted_terms(self, view, app_request, mocker):
        mock_session = mocker.patch("benefits.metro_mobility_wallet.mixins.Session")
        mock_session.return_value.accepted_terms = True

        response = view.dispatch(app_request)

        assert response == "Success"
