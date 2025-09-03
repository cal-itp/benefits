from django.urls import reverse

import pytest

from benefits.routes import routes
import benefits.core.session
from benefits.eligibility.forms import EnrollmentFlowSelectionForm, EligibilityVerificationForm
import benefits.eligibility.views as views


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
    return {"sub": "A1234567", "name": "Person"}


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
    def view(self, app_request, mocked_eligibility_request_session):
        """Fixture to create an instance of StartView."""
        v = views.StartView()
        v.setup(app_request)
        return v

    def test_template_name(self, view):
        assert view.template_name == "eligibility/start.html"

    def test_get_context_data(self, view, app_request, model_EnrollmentFlow):
        view.dispatch(app_request)
        context = view.get_context_data()

        for key, value in model_EnrollmentFlow.eligibility_start_context.items():
            assert context[key] == value

    def test_get(self, mocker, view, app_request, mocked_session_update):
        # spy on the call to get() but call dispatch() like a real request
        spy = mocker.spy(view, "get")
        response = view.dispatch(app_request)

        spy.assert_called_once()
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

    def test_post_form_invalid(self, view, app_request, invalid_form_data, mocked_analytics_module):
        app_request.POST = invalid_form_data

        response = view.post(app_request)

        mocked_analytics_module.started_eligibility.assert_called_once()
        assert response.status_code == 200
        assert response.template_name == ["eligibility/confirm.html"]

    def test_post_recaptcha_fail(self, mocker, view, app_request):
        mocker.patch("benefits.eligibility.views.recaptcha.has_error", return_value=True)
        messages = mocker.spy(views, "messages")

        response = view.post(app_request)
        assert response.status_code == 200
        assert response.template_name == ["eligibility/confirm.html"]
        messages.error.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request", "model_EnrollmentFlow_with_eligibility_api")
def test_confirm_post_valid_form_eligibility_error(mocker, client, form_data, mocked_analytics_module):
    mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=None)

    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.post(path, form_data)

    mocked_analytics_module.returned_error.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == ["eligibility/confirm.html"]


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request", "model_EnrollmentFlow_with_eligibility_api")
def test_confirm_post_valid_form_eligibility_unverified(mocker, client, form_data):
    mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=[])

    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.post(path, form_data)

    assert response.status_code == 302
    assert response.url == reverse(routes.ELIGIBILITY_UNVERIFIED)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request", "model_EnrollmentFlow_with_eligibility_api")
def test_confirm_post_valid_form_eligibility_verified(
    mocker,
    client,
    form_data,
    mocked_session_eligible,
    mocked_session_update,
    mocked_analytics_module,
):
    eligible = mocked_session_eligible.return_value
    mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=eligible)

    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.post(path, form_data)

    assert response.status_code == 302
    assert response.url == reverse(routes.ENROLLMENT_INDEX)
    mocked_session_update.assert_called_once()
    mocked_analytics_module.returned_success.assert_called_once()


@pytest.mark.django_db
class TestUnverifiedView:
    @pytest.fixture
    def view(self, app_request, mocked_eligibility_request_session):
        v = views.UnverifiedView()
        v.setup(app_request)
        return v

    def test_view(self, view):
        assert view.template_name == "eligibility/unverified.html"

    def test_get_context_data__dispatched(self, view, app_request, model_EnrollmentFlow):
        view.dispatch(app_request)

        ctx = view.get_context_data()

        for key, value in model_EnrollmentFlow.eligibility_unverified_context.items():
            assert ctx[key] == value

    def test_get_context_data__not_dispatched(self, view, model_EnrollmentFlow):
        with pytest.raises(AttributeError, match="object has no attribute 'flow'"):
            view.get_context_data()

    def test_get(self, mocker, view, app_request, mocked_analytics_module):
        # spy on the call to get() but call dispatch() like a real request
        spy = mocker.spy(view, "get")
        response = view.dispatch(app_request)

        spy.assert_called_once()
        assert response.status_code == 200
        mocked_analytics_module.returned_fail.assert_called_once()
