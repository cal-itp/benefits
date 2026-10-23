import pytest
from django.urls import reverse

import benefits.metro_mobility_wallet.views as views
from benefits.metro_mobility_wallet.session import Session


@pytest.fixture
def mocked_session_terms(mocker):
    session = mocker.Mock(spec=Session)
    mocker.patch("benefits.metro_mobility_wallet.views.eligibility.Session", return_value=session)
    return session


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

    def test_form_valid(self, view, mocked_session_terms):
        form = view.form_class(data={"agree_to_terms": True})

        assert form.is_valid()
        response = view.form_valid(form)

        assert mocked_session_terms.agreed_to_terms is True
        assert response.url == reverse("metro_mobility_wallet:apply")


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


class TestSuccessView:
    @pytest.fixture
    def view(self, app_request):
        v = views.SuccessView()
        v.setup(app_request)
        return v

    def test_template_name(self, view):
        assert view.template_name == "metro_mobility_wallet/success.html"
