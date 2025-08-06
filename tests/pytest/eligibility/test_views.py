from django.http import HttpResponse
from django.urls import reverse

import pytest

from benefits.core import models
from benefits.routes import routes
from benefits.core.middleware import TEMPLATE_USER_ERROR
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
def mocked_VerifiedView(mocker):
    return mocker.patch.object(views, "VerifiedView")


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


@pytest.fixture
def model_EnrollmentFlow_with_form_class(mocker, model_EnrollmentFlow_with_eligibility_api):
    model_EnrollmentFlow_with_eligibility_api.eligibility_form_class = f"{__name__}.SampleVerificationForm"
    model_EnrollmentFlow_with_eligibility_api.save()
    mocker.patch("benefits.eligibility.views.session.flow", return_value=model_EnrollmentFlow_with_eligibility_api)
    return model_EnrollmentFlow_with_eligibility_api


@pytest.mark.django_db
def test_index_filtering_flows(mocker, model_TransitAgency, client):
    digital = models.EnrollmentFlow.objects.create(
        transit_agency=model_TransitAgency,
        supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL],
        label="Digital",
        selection_label_template_override="eligibility/includes/selection-label.html",
    )
    in_person = models.EnrollmentFlow.objects.create(
        transit_agency=model_TransitAgency,
        supported_enrollment_methods=[models.EnrollmentMethods.IN_PERSON],
        label="In-Person",
        selection_label_template_override="eligibility/includes/selection-label.html",
    )
    both = models.EnrollmentFlow.objects.create(
        transit_agency=model_TransitAgency,
        supported_enrollment_methods=[models.EnrollmentMethods.DIGITAL, models.EnrollmentMethods.IN_PERSON],
        label="Both",
        selection_label_template_override="eligibility/includes/selection-label.html",
    )
    mocker.patch("benefits.core.session.agency", autospec=True, return_value=model_TransitAgency)

    path = reverse(routes.ELIGIBILITY_INDEX)
    response = client.get(path)
    filtered_flow_ids = [choice[0] for choice in response.context_data["form"].fields["flow"].choices]

    assert digital.id, both.id in filtered_flow_ids
    assert in_person.id not in filtered_flow_ids


@pytest.mark.django_db
@pytest.mark.usefixtures("model_LittlepayConfig")
def test_index_get_agency_multiple_flows(mocker, model_TransitAgency, model_EnrollmentFlow, mocked_session_agency, client):
    # override the mocked session agency with a mock agency that has multiple flows
    mock_agency = mocker.Mock(spec=model_TransitAgency)

    # mock the enrollment_flows property on the class - https://stackoverflow.com/a/55642462
    mock_manager = mocker.Mock()
    mock_manager.all.return_value = [model_EnrollmentFlow, model_EnrollmentFlow]
    type(mock_agency).enrollment_flows = mocker.PropertyMock(return_value=mock_manager)
    type(mock_agency).enrollment_flows.filter.return_value = [model_EnrollmentFlow, model_EnrollmentFlow]
    type(mock_agency).eligibility_index_context = mocker.PropertyMock(return_value=dict(form_text="copy goes here"))

    mocked_session_agency.return_value = mock_agency

    path = reverse(routes.ELIGIBILITY_INDEX)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == ["eligibility/index.html"]
    assert "form" in response.context_data
    assert isinstance(response.context_data["form"], EnrollmentFlowSelectionForm)


@pytest.mark.django_db
@pytest.mark.usefixtures("model_LittlepayConfig")
def test_index_get_agency_single_flow(mocker, model_TransitAgency, model_EnrollmentFlow, mocked_session_agency, client):
    # override the mocked session agency with a mock agency that has a single flow
    mock_agency = mocker.Mock(spec=model_TransitAgency)

    # mock the enrollment_flows property on the class - https://stackoverflow.com/a/55642462
    mock_manager = mocker.Mock()
    mock_manager.all.return_value = [model_EnrollmentFlow]
    type(mock_agency).enrollment_flows = mocker.PropertyMock(return_value=mock_manager)
    type(mock_agency).enrollment_flows.filter.return_value = [model_EnrollmentFlow, model_EnrollmentFlow]
    type(mock_agency).eligibility_index_context = mocker.PropertyMock(return_value=dict(form_text="copy goes here"))

    mocked_session_agency.return_value = mock_agency

    path = reverse(routes.ELIGIBILITY_INDEX)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == ["eligibility/index.html"]
    assert "form" in response.context_data
    assert isinstance(response.context_data["form"], EnrollmentFlowSelectionForm)


@pytest.mark.django_db
def test_index_get_without_agency(client):
    path = reverse(routes.ELIGIBILITY_INDEX)

    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_USER_ERROR


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_index_post_invalid_form(client):
    path = reverse(routes.ELIGIBILITY_INDEX)

    response = client.post(path, {"invalid": "data"})

    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_index_post_valid_form(client, model_EnrollmentFlow, mocked_session_update, mocked_analytics_module):
    path = reverse(routes.ELIGIBILITY_INDEX)

    response = client.post(path, {"flow": model_EnrollmentFlow.id})

    assert response.status_code == 302
    assert response.url == reverse(routes.ELIGIBILITY_START)
    assert mocked_session_update.call_args.kwargs["flow"] == model_EnrollmentFlow
    mocked_analytics_module.selected_flow.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request")
def test_index_calls_session_logout(client, session_logout_spy):
    path = reverse(routes.ELIGIBILITY_INDEX)

    client.get(path)

    session_logout_spy.assert_called_once()


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
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow")
def test_confirm_get_unverified(mocker, client):
    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.get(path)

    assert response.status_code == 200
    assert response.template_name == views.TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_eligible", "mocked_session_flow")
def test_confirm_get_verified(client, mocked_session_update, mocked_VerifiedView):
    mocked_view = mocked_VerifiedView.return_value
    mocked_view.setup_and_dispatch.return_value = HttpResponse(status=200)

    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.get(path)

    mocked_VerifiedView.assert_called_once()
    mocked_view.setup_and_dispatch.assert_called_once()
    assert response == mocked_view.setup_and_dispatch.return_value


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request", "model_EnrollmentFlow_with_form_class")
def test_confirm_post_invalid_form(client, invalid_form_data, mocked_analytics_module):
    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.post(path, invalid_form_data)

    mocked_analytics_module.started_eligibility.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == views.TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_analytics_module", "mocked_eligibility_auth_request", "model_EnrollmentFlow_with_form_class")
def test_confirm_post_recaptcha_fail(mocker, client, invalid_form_data):
    mocker.patch("benefits.eligibility.views.recaptcha.has_error", return_value=True)
    messages = mocker.spy(views, "messages")

    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.post(path, invalid_form_data)

    assert response.status_code == 200
    assert response.template_name == views.TEMPLATE_CONFIRM
    messages.error.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request", "model_EnrollmentFlow_with_form_class")
def test_confirm_post_valid_form_eligibility_error(mocker, client, form_data, mocked_analytics_module):
    mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=None)

    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.post(path, form_data)

    mocked_analytics_module.returned_error.assert_called_once()
    assert response.status_code == 200
    assert response.template_name == views.TEMPLATE_CONFIRM


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request", "model_EnrollmentFlow_with_form_class")
def test_confirm_post_valid_form_eligibility_unverified(mocker, client, form_data):
    mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=[])

    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.post(path, form_data)

    assert response.status_code == 302
    assert response.url == reverse(routes.ELIGIBILITY_UNVERIFIED)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_eligibility_auth_request", "model_EnrollmentFlow_with_form_class")
def test_confirm_post_valid_form_eligibility_verified(
    mocker, client, form_data, mocked_session_eligible, mocked_session_update, mocked_VerifiedView, mocked_analytics_module
):
    mocked_view = mocked_VerifiedView.return_value
    mocked_view.setup_and_dispatch.return_value = HttpResponse(status=200)

    eligible = mocked_session_eligible.return_value
    mocker.patch("benefits.eligibility.verify.eligibility_from_api", return_value=eligible)

    path = reverse(routes.ELIGIBILITY_CONFIRM)
    response = client.post(path, form_data)

    mocked_VerifiedView.assert_called_once()
    mocked_view.setup_and_dispatch.assert_called_once()
    assert response == mocked_view.setup_and_dispatch.return_value


@pytest.mark.django_db
class TestVerifiedView:
    @pytest.fixture
    def view(self, app_request, mocked_eligibility_request_session):
        v = views.VerifiedView()
        v.setup(app_request)
        return v

    def test_get_redirect_url(self, view):
        assert view.get_redirect_url() == reverse(routes.ENROLLMENT_INDEX)

    def test_post(self, mocker, view, app_request_post, mocked_session_update, mocked_analytics_module):
        # spy on the call to post() but call dispatch() like a real request
        spy = mocker.spy(view, "post")
        response = view.dispatch(app_request_post)

        spy.assert_called_once()
        assert response.status_code == 302
        mocked_session_update.assert_called_once_with(app_request_post, eligible=True)
        mocked_analytics_module.returned_success.assert_called_once()

    def test_setup_and_dispatch(self, mocker, view, app_request_post):
        spy_setup = mocker.spy(view, "setup")
        spy_dispatch = mocker.spy(view, "dispatch")

        response = view.setup_and_dispatch(app_request_post)

        spy_setup.assert_called_once_with(app_request_post)
        spy_dispatch.assert_called_once_with(app_request_post)
        assert response.status_code == 302


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
