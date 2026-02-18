import pytest
from django.urls import reverse

import benefits.core.session
import benefits.eligibility.views as views
from benefits.core.models import SystemName
from benefits.eligibility import forms
from benefits.eligibility.forms import EligibilityVerificationForm, EnrollmentFlowSelectionForm
from benefits.routes import routes


@pytest.fixture
def mocked_analytics_module(mocked_analytics_module):
    return mocked_analytics_module(views)


@pytest.fixture
def mocked_eligibility_auth_request(mocked_eligibility_request_session, mocked_session_logged_in):
    """
    Stub fixture combines mocked_eligibility_request_session and mocked_session_logged_in
    so that session behaves like in an authenticated request to the eligibility app
    """
    pass


@pytest.fixture
def session_logout_spy(mocker):
    return mocker.spy(benefits.core.session, "logout")


@pytest.fixture
def mocked_flow_selection_form(mocker):
    mock_form = mocker.Mock(spec=EnrollmentFlowSelectionForm)
    mocker.patch("benefits.eligibility.views.forms.EnrollmentFlowSelectionForm", return_value=mock_form)


@pytest.fixture
def form_data():
    return {"sub": "12345", "name": "Person"}


@pytest.fixture
def invalid_form_data():
    return {"invalid": "data"}


class SampleVerificationForm(EligibilityVerificationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(
            "title",
            "headline",
            "blurb",
            "name_label",
            "name_placeholder",
            "name_help_text",
            "sub_label",
            "sub_placeholder",
            "sub_help_text",
            *args,
            **kwargs,
        )


@pytest.mark.django_db
class TestIndexView:
    @pytest.fixture
    def view(self, app_request, mocked_session_agency):
        v = views.IndexView()
        v.setup(app_request)
        v.agency = mocked_session_agency(app_request)
        return v

    def test_get_form_kwargs(self, view):
        kwargs = view.get_form_kwargs()
        assert kwargs["agency"] == view.agency

    def test_get_context_data(self, view):
        context_data = view.get_context_data()
        assert "form_text" in context_data

    def test_get(self, view, app_request, session_logout_spy):
        view.get(app_request)

        session_logout_spy.assert_called_once()

    def test_form_valid(self, view, model_EnrollmentFlow, mocked_session_update, mocked_analytics_module):
        form = view.form_class(data=dict(flow=model_EnrollmentFlow.id), agency=view.agency)

        assert form.is_valid()
        view.form_valid(form)

        assert mocked_session_update.call_args.kwargs["flow"] == model_EnrollmentFlow
        mocked_analytics_module.selected_flow.assert_called_once()


@pytest.mark.django_db
class TestStartView:
    @pytest.fixture
    def view(self, app_request, model_EnrollmentFlow):
        """Fixture to create an instance of StartView."""
        v = views.StartView()
        v.setup(app_request)
        v.flow = model_EnrollmentFlow
        return v

    def test_template_name(self, view):
        assert view.template_name == "eligibility/start.html"

    def test_get_context_data(self, view):
        context = view.get_context_data()

        assert "page_title" in context
        assert "headline_text" in context
        assert "eligibility_item_headline" in context
        assert "eligibility_item_body" in context
        assert "call_to_action_button" in context

    def test_get(self, view, app_request, mocked_session_update):
        response = view.get(app_request)

        assert response.status_code == 200
        mocked_session_update.assert_called_once()


@pytest.mark.django_db
class TestConfirmView:
    @pytest.fixture
    def view(
        self,
        app_request,
        mocked_session_agency,
        mocked_session_flow,
        model_EnrollmentFlow_with_eligibility_api,
    ):
        """Fixture to create an instance of ConfirmView."""
        v = views.ConfirmView()
        v.setup(app_request)
        v.agency = mocked_session_agency(app_request)
        v.flow = mocked_session_flow(app_request)
        return v

    @pytest.mark.parametrize(
        "flow_system_name, expected_form_class",
        [
            (SystemName.COURTESY_CARD, forms.MSTCourtesyCard),
            (SystemName.REDUCED_FARE_MOBILITY_ID, forms.SBMTDMobilityPass),
        ],
    )
    def test_get_form_class_valid(self, view, flow_system_name, expected_form_class):
        view.flow.system_name = flow_system_name

        form_class = view.get_form_class()

        assert form_class == expected_form_class

    def test_get_form_class_invalid(self, view):
        view.flow.system_name = "senior"
        expected_error_msg = f"The {view.flow.system_name} flow does not support Eligibility API verification."
        with pytest.raises(ValueError, match=expected_error_msg):
            view.get_form_class()

    def test_get(self, view, app_request):
        response = view.get(app_request)

        assert benefits.core.session.origin(app_request) == reverse(routes.ELIGIBILITY_CONFIRM)
        assert response.status_code == 200
        assert response.template_name == ["eligibility/confirm.html"]

    @pytest.mark.usefixtures("mocked_session_eligible")
    def test_get_already_eligible(self, view, app_request):
        response = view.get(app_request)

        assert response.status_code == 302
        assert response.url == reverse(routes.ENROLLMENT_INDEX)

    def test_post(self, view, app_request, mocked_analytics_module):
        view.post(app_request)

        mocked_analytics_module.started_eligibility.assert_called_once()

    def test_form_invalid(self, view, invalid_form_data):
        form_class = view.get_form_class()
        form = form_class(data=invalid_form_data)

        response = view.form_invalid(form)

        assert response.status_code == 200
        assert response.template_name == ["eligibility/confirm.html"]

    def test_form_invalid_recaptcha_fail(self, mocker, view, invalid_form_data):
        mocker.patch("benefits.eligibility.views.recaptcha.has_error", return_value=True)
        messages = mocker.spy(views, "messages")

        form_class = view.get_form_class()
        form = form_class(data=invalid_form_data)

        response = view.form_invalid(form)

        assert response.status_code == 200
        assert response.template_name == ["eligibility/confirm.html"]
        messages.error.assert_called_once()

    def test_form_valid_eligibility_error(self, mocker, view, form_data, mocked_analytics_module):
        mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=None)

        form_class = view.get_form_class()
        form = form_class(data=form_data)

        response = view.form_valid(form)

        mocked_analytics_module.returned_error.assert_called_once()
        assert response.status_code == 200
        assert response.template_name == ["eligibility/confirm.html"]

    def test_form_valid_unverified(self, mocker, view, form_data):
        mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=False)

        form_class = view.get_form_class()
        form = form_class(data=form_data)

        response = view.form_valid(form)

        assert response.status_code == 302
        assert response.url == reverse(routes.ELIGIBILITY_UNVERIFIED)

    def test_form_valid_verified(self, mocker, view, form_data, mocked_session_update, mocked_analytics_module):
        mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=True)

        form_class = view.get_form_class()
        form = form_class(data=form_data)

        response = view.form_valid(form)

        assert response.status_code == 302
        assert response.url == reverse(routes.ENROLLMENT_INDEX)
        mocked_session_update.assert_called_once()
        mocked_analytics_module.returned_success.assert_called_once()


@pytest.mark.django_db
class TestUnverifiedView:
    @pytest.fixture
    def view(self, app_request, model_EnrollmentFlow):
        v = views.UnverifiedView()
        v.setup(app_request)

        model_EnrollmentFlow.system_name = SystemName.COURTESY_CARD
        v.flow = model_EnrollmentFlow
        return v

    def test_view(self, view):
        assert view.template_name == "eligibility/unverified.html"

    def test_get_context_data(self, view):
        context = view.get_context_data()

        assert "headline_text" in context
        assert "body_text" in context
        assert "button_text" in context

    def test_get(self, mocker, view, app_request, mocked_analytics_module):
        response = view.get(app_request)

        assert response.status_code == 200
        mocked_analytics_module.returned_fail.assert_called_once()
