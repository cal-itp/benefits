import pytest

from django.urls import reverse

from benefits.core.admin import views


@pytest.mark.django_db
class TestBenefitsPasswordResetView:

    @pytest.fixture
    def view(self, app_request):
        """Fixture to create an instance of BenefitsPasswordResetView."""
        v = views.BenefitsPasswordResetView()
        v.setup(app_request)
        return v

    def test_form_valid(self, view):
        email = "mail@example.com"
        form = view.form_class(data={"email": email})
        assert form.is_valid()

        view.form_valid(form)
        assert view.success_url == f"{reverse("password_reset_done")}?email={email}"


@pytest.mark.django_db
class TestBenefitsPasswordResetDoneView:
    @pytest.fixture
    def view(self, app_request):
        """Fixture to create an instance of BenefitsPasswordResetDoneView."""
        v = views.BenefitsPasswordResetDoneView()
        v.setup(app_request)
        return v

    def test_get_context_data(self, view):
        context_data = view.get_context_data()
        assert "email" in context_data
