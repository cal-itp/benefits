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
