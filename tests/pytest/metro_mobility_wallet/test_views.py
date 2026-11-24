import pytest
from cdt_identity.claims import ClaimsResult
from cdt_identity.session import Session as OAuthSession
from django.urls import reverse

import benefits.metro_mobility_wallet.views as views
from benefits.core.models.enrollment import EnrollmentFlow, SystemName
from benefits.metro_mobility_wallet.session import Session


@pytest.fixture
def mocked_session_terms(mocker):
    session = mocker.Mock(spec=Session)
    mocker.patch("benefits.metro_mobility_wallet.views.eligibility.Session", return_value=session)
    return session


@pytest.fixture
def model_ClaimsVerificationRequest_with_extra_claims(model_ClaimsVerificationRequest):
    model_ClaimsVerificationRequest.extra_claims = "given_name family_name email phone_number"
    model_ClaimsVerificationRequest.save()

    return model_ClaimsVerificationRequest


@pytest.fixture
def form_data():
    return {"email": "mail@example.com", "phone_number": "987-654-3210"}


@pytest.fixture
def invalid_form_data():
    return {"email": "mail@example", "phone_number": "abc-123-@#$%"}


@pytest.mark.django_db
class TestIndexView:

    @pytest.fixture
    def model_metro_EnrollmentFlow(self, model_IdentityGatewayConfig):
        return EnrollmentFlow.objects.create(
            system_name=SystemName.METRO_MOBILITY_WALLET, oauth_config=model_IdentityGatewayConfig
        )

    @pytest.fixture
    def view(self, app_request):
        v = views.IndexView()
        v.setup(app_request)
        return v

    def test_template_name(self, view):
        assert view.template_name == "metro_mobility_wallet/index.html"

    @pytest.mark.usefixtures("model_metro_EnrollmentFlow")
    def test_get(self, view, app_request, mocker, mocked_session_reset):
        mock_session = mocker.patch("benefits.metro_mobility_wallet.views.index.Session")

        response = view.get(app_request)

        assert response.status_code == 200
        mock_session.assert_called_once_with(app_request)
        mocked_session_reset.assert_called_once_with(app_request)


class TestTermsView:
    @pytest.fixture
    def view(self, app_request):
        v = views.TermsView()
        v.setup(app_request)
        return v

    def test_template_name(self, view):
        assert view.template_name == "metro_mobility_wallet/terms.html"

    def test_form_valid(self, view, mocked_session_terms):
        form = view.form_class(data={"accepted_terms": True})

        assert form.is_valid()
        response = view.form_valid(form)

        assert mocked_session_terms.accepted_terms is True
        assert response.url == reverse("metro_mobility_wallet:apply")


class TestApplyView:
    @pytest.fixture
    def view(self, app_request):
        v = views.ApplyView()
        v.setup(app_request)
        return v

    def test_template_name(self, view):
        assert view.template_name == "metro_mobility_wallet/apply.html"

    def test_get_context_data(self, view):
        context_data = view.get_context_data()
        cta_button = context_data["call_to_action_button"]

        assert cta_button.text == "Apply with"
        assert cta_button.fallback_text == "Login.gov"
        assert cta_button.route == "metro_mobility_wallet:cdt:login"
        assert cta_button.extra_classes == "login"


class TestConfirmationView:
    @pytest.fixture
    def view(self, app_request):
        v = views.ConfirmationView()
        v.setup(app_request)
        return v

    @pytest.fixture
    def extra_claims_result(self):
        return ClaimsResult(
            verified={
                "given_name": "Marty",
                "family_name": "Ail",
                "email": "mail@example.com",
                "phone_number": "+19876543210",
            }
        )

    def test_template_name(self, view):
        assert view.template_name == "metro_mobility_wallet/confirmation.html"

    @pytest.mark.django_db
    def test_get(self, view, app_request, model_ClaimsVerificationRequest_with_extra_claims, extra_claims_result):
        OAuthSession(
            app_request,
            claims_request=model_ClaimsVerificationRequest_with_extra_claims,
            claims_result=extra_claims_result,
        )

        view.get(app_request)

        assert view.initial == {
            "email": "mail@example.com",
            "phone_number": "987-654-3210",
        }

    @pytest.mark.django_db
    def test_get_context_data(self, view, app_request, model_ClaimsVerificationRequest_with_extra_claims, extra_claims_result):
        OAuthSession(
            app_request,
            claims_request=model_ClaimsVerificationRequest_with_extra_claims,
            claims_result=extra_claims_result,
        )

        view.get(app_request)

        context_data = view.get_context_data()
        first_name = context_data["first_name"]
        last_name = context_data["last_name"]
        cta_button = context_data["call_to_action_button"]

        assert first_name == "Marty"
        assert last_name == "Ail"
        assert cta_button.text == "Submit"
        assert cta_button.route == "metro_mobility_wallet:confirmation"

    def test_form_valid(self, mocker, view, form_data, mocked_session_update, mocked_analytics_module):
        # mocker.patch("benefits.metro_mobility_wallet.submittable...", return_value=True)

        form_class = view.get_form_class()
        form = form_class(data=form_data)

        response = view.form_valid(form)

        assert response.status_code == 302
        assert response.url == reverse("metro_mobility_wallet:success")

        # mocked_session_update.assert_called_once()
        # mocked_analytics_module.returned_success.assert_called_once()

    def test_form_invalid(self, mocker, view, invalid_form_data):
        mocker.patch(
            "benefits.core.session.oauth_extra_claims_dict", return_value={"given_name": "Marty", "family_name": "Ail"}
        )

        form_class = view.get_form_class()
        form = form_class(data=invalid_form_data)

        response = view.form_invalid(form)

        assert response.status_code == 200
        assert response.template_name == ["metro_mobility_wallet/confirmation.html"]

    def test_form_invalid_recaptcha_fail(self, mocker, view, invalid_form_data):
        mocker.patch(
            "benefits.core.session.oauth_extra_claims_dict", return_value={"given_name": "Marty", "family_name": "Ail"}
        )
        mocker.patch("benefits.metro_mobility_wallet.views.enrollment.recaptcha.has_error", return_value=True)
        messages = mocker.spy(views.enrollment, "messages")

        form_class = view.get_form_class()
        form = form_class(data=invalid_form_data)

        response = view.form_invalid(form)

        assert response.status_code == 200
        assert response.template_name == ["metro_mobility_wallet/confirmation.html"]
        messages.error.assert_called_once()


class TestSuccessView:
    @pytest.fixture
    def view(self, app_request):
        v = views.SuccessView()
        v.setup(app_request)
        return v

    def test_template_name(self, view):
        assert view.template_name == "metro_mobility_wallet/success.html"
