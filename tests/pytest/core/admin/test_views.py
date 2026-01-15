import base64

import pytest
from django.contrib.messages.middleware import MessageMiddleware
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
        email = "mail+alias@example.com"
        form = view.form_class(data={"email": email})
        assert form.is_valid()

        view.form_valid(form)
        assert view.success_url == f"{reverse("password_reset_done")}?email=mail%2Balias%40example.com"


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


@pytest.mark.django_db
class TestBenefitsPasswordResetConfirmView:
    @pytest.fixture
    def view(self, app_request, model_User):
        """Fixture to create an instance of BenefitsPasswordResetConfirmView."""
        v = views.BenefitsPasswordResetConfirmView()
        v.setup(app_request)

        # Enable the Django messages framework
        middleware = MessageMiddleware(get_response=lambda request: None)
        middleware.process_request(app_request)

        # Add a mocked token to the session
        user_b64 = base64.b64encode(f"{model_User.id}".encode())
        user_b64_str = user_b64.decode("ascii")
        app_request.session["_password_reset_token"] = user_b64_str[:-2] if user_b64_str[-2:] == "==" else user_b64_str
        app_request.session.save()

        return v

    def test_form_valid(self, view, model_User, mocker):
        form = view.form_class(model_User, data={"new_password1": "testPW123!", "new_password2": "testPW123!"})
        assert form.is_valid()

        view.form_valid(form)

        messages = list(view.request._messages)
        assert len(messages) == 1
        assert messages[0].tags == "success"
        assert str(messages[0]) == "Your password has been reset. Please log in."
