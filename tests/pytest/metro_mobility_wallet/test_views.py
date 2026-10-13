import pytest

import benefits.metro_mobility_wallet.views as views


class TestIndexView:
    @pytest.fixture
    def view(self, app_request):
        v = views.IndexView()
        v.setup(app_request)
        return v

    def test_template_name(self, view):
        assert view.template_name == "metro_mobility_wallet/index.html"


class TestTermsView:
    @pytest.fixture
    def view(self, app_request):
        v = views.TermsView()
        v.setup(app_request)
        return v

    def test_template_name(self, view):
        assert view.template_name == "metro_mobility_wallet/terms.html"


class TestApplyView:
    @pytest.fixture
    def view(self, app_request):
        v = views.ApplyView()
        v.setup(app_request)
        return v

    def test_template_name(self, view):
        assert view.template_name == "metro_mobility_wallet/apply.html"


class TestConfirmationView:
    @pytest.fixture
    def view(self, app_request):
        v = views.ConfirmationView()
        v.setup(app_request)
        return v

    def test_template_name(self, view):
        assert view.template_name == "metro_mobility_wallet/confirmation.html"
