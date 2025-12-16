import pytest
from django.urls import reverse


from benefits.core import models
from benefits.in_person import forms
import benefits.in_person.views as views
from benefits.routes import routes


@pytest.fixture
def card_tokenize_form_data():
    return {"card_token": "tokenized_card"}


@pytest.fixture
def invalid_form_data():
    return {"invalid": "data"}


@pytest.fixture
def mocked_eligibility_analytics_module(mocker):
    return mocker.patch.object(views, "eligibility_analytics")


@pytest.fixture
def mocked_enrollment_analytics_module(mocker):
    return mocker.patch.object(views, "enrollment_analytics")


@pytest.fixture
def mocked_sentry_sdk_module(mocker):
    return mocker.patch.object(views, "sentry_sdk")


@pytest.fixture
def mocked_session_module(mocker):
    return mocker.patch.object(views, "session")


@pytest.fixture
def mocked_transit_agency_class(mocker):
    return mocker.patch.object(views, "TransitAgency")


@pytest.fixture
def mocked_session_agency_littlepay(mocker, model_TransitAgency, model_LittlepayConfig):
    model_LittlepayConfig.transit_agency = model_TransitAgency
    model_TransitAgency.save()
    return mocker.patch("benefits.core.session.agency", autospec=True, return_value=model_TransitAgency)


@pytest.mark.django_db
@pytest.mark.parametrize("viewname", [routes.IN_PERSON_ELIGIBILITY, routes.IN_PERSON_ENROLLMENT])
def test_view_not_logged_in(client, viewname):
    path = reverse(viewname)

    response = client.get(path)
    assert response.status_code == 302
    assert response.url == "/admin/login/?next=" + path


@pytest.mark.django_db
class TestEligibilityView:
    @pytest.fixture
    def view(self, model_User, app_request, mocked_session_agency):
        # manually attach a logged-in user to the request
        app_request.user = model_User

        v = views.EligibilityView()
        v.setup(app_request)
        v.agency = mocked_session_agency(app_request)
        return v

    def test_get_form_kwargs(self, view):
        kwargs = view.get_form_kwargs()
        assert kwargs["agency"] == view.agency

    def test_get_context_data(self, view):
        context_data = view.get_context_data()
        assert "title" in context_data

    def test_dispatch(self, view, mocker):
        littlepay_session = mocker.patch.object(views, "LittlepaySession")
        switchio_session = mocker.patch.object(views, "SwitchioSession")

        view.dispatch(view.request)

        littlepay_session.assert_called_once_with(view.request, reset=True)
        switchio_session.assert_called_once_with(view.request, reset=True)

    def test_dispatch_no_agency_in_session(
        self, view, mocked_session_module, mocked_transit_agency_class, model_TransitAgency
    ):
        view.agency = None
        mocked_session_module.agency.return_value = None
        mocked_transit_agency_class.for_user.return_value = model_TransitAgency

        view.dispatch(view.request)

        mocked_session_module.update.assert_called_once()
        assert view.agency == model_TransitAgency

    def test_form_valid(self, view, mocker, model_EnrollmentFlow, mocked_session_module, mocked_eligibility_analytics_module):
        mock_enrollment_flow_model = mocker.patch.object(models.EnrollmentFlow.objects, "get")
        mock_enrollment_flow_model.return_value = model_EnrollmentFlow

        mock_form = mocker.Mock()
        mock_form.cleaned_data = {"flow": model_EnrollmentFlow.id}

        response = view.form_valid(mock_form)

        mock_enrollment_flow_model.assert_called_once_with(id=model_EnrollmentFlow.id)
        mocked_session_module.update.assert_called_once_with(view.request, flow=model_EnrollmentFlow, eligible=True)
        mocked_eligibility_analytics_module.selected_flow.assert_called_once_with(
            view.request, model_EnrollmentFlow, enrollment_method=models.EnrollmentMethods.IN_PERSON
        )
        mocked_eligibility_analytics_module.started_eligibility.assert_called_once_with(
            view.request, model_EnrollmentFlow, enrollment_method=models.EnrollmentMethods.IN_PERSON
        )
        mocked_eligibility_analytics_module.returned_success.assert_called_once_with(
            view.request, model_EnrollmentFlow, enrollment_method=models.EnrollmentMethods.IN_PERSON
        )
        assert response.status_code == 302
        assert response.url == reverse(routes.IN_PERSON_ENROLLMENT)


@pytest.mark.django_db
class TestEnrollmentView:
    @pytest.fixture
    def view(self, app_request, mocked_session_agency_littlepay):
        v = views.EnrollmentView()
        v.setup(app_request)
        v.agency = mocked_session_agency_littlepay(app_request)
        return v

    def test_get_redirect_url_for_littlepay(self, view):
        assert view.get_redirect_url() == reverse(view.agency.in_person_enrollment_index_route)


@pytest.mark.django_db
class TestLittlepayEnrollmentView:
    @pytest.fixture
    def view(self, app_request, model_LittlepayConfig, model_EnrollmentFlow, model_User):
        app_request.user = model_User
        v = views.LittlepayEnrollmentView()
        v.setup(app_request)
        v.agency = model_LittlepayConfig.transit_agency
        v.flow = model_EnrollmentFlow
        return v

    def test_get_verified_by(self, mocker, app_request, view):
        app_request.user = mocker.Mock(first_name="First", last_name="Last")

        assert view._get_verified_by() == "First Last"

    def test_get_context_data(self, view):
        context = view.get_context_data()

        assert "title" in context


@pytest.mark.django_db
class TestReenrollmentErrorView:
    @pytest.fixture
    def view(self, app_request, model_LittlepayConfig, model_EnrollmentFlow, model_User):
        app_request.user = model_User
        v = views.ReenrollmentErrorView()
        v.setup(app_request)
        v.agency = model_LittlepayConfig.transit_agency
        v.flow = model_EnrollmentFlow
        return v

    def test_get_context_data(self, view):
        context = view.get_context_data()

        assert "title" in context
        assert context["flow_label"] == view.flow.label


@pytest.mark.django_db
class TestSystemErrorView:
    @pytest.fixture
    def view(self, app_request, model_LittlepayConfig, model_EnrollmentFlow, model_User):
        app_request.user = model_User
        v = views.SystemErrorView()
        v.setup(app_request)
        v.agency = model_LittlepayConfig.transit_agency
        v.flow = model_EnrollmentFlow
        return v

    def test_get_origin_url(self, view):
        assert view.get_origin_url() == reverse(routes.ADMIN_INDEX)


@pytest.mark.django_db
class TestServerErrorView:
    @pytest.fixture
    def view(self, app_request, model_LittlepayConfig, model_User):
        app_request.user = model_User
        v = views.ServerErrorView()
        v.setup(app_request)
        v.agency = model_LittlepayConfig.transit_agency
        return v

    def test_post(self, app_request_post, view):
        response = view.post(app_request_post)

        assert response.status_code == 200
        assert response.template_name == ["in_person/enrollment/server_error.html"]


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow", "mocked_session_agency")
def test_success(admin_client):
    path = reverse(routes.IN_PERSON_ENROLLMENT_SUCCESS)

    response = admin_client.get(path)

    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment/success.html"


@pytest.mark.django_db
class TestSwitchioGatewayUrlView:
    @pytest.fixture
    def view(self, app_request, model_SwitchioConfig):
        v = views.SwitchioGatewayUrlView()
        v.setup(app_request)
        v.agency = model_SwitchioConfig.transit_agency
        return v

    def test_view(self, view: views.SwitchioGatewayUrlView):
        assert view.enrollment_method == models.EnrollmentMethods.IN_PERSON
        assert view.route_redirect == routes.IN_PERSON_ENROLLMENT_SWITCHIO_INDEX
        assert view.route_system_error == routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR
        assert view.route_server_error == routes.IN_PERSON_SERVER_ERROR


@pytest.mark.django_db
class TestSwitchioEnrollmentIndexView:
    @pytest.fixture
    def view(self, app_request, model_SwitchioConfig, model_EnrollmentFlow, model_User):
        app_request.user = model_User
        v = views.SwitchioEnrollmentIndexView()
        v.setup(app_request)
        v.agency = model_SwitchioConfig.transit_agency
        v.flow = model_EnrollmentFlow
        return v

    def test_view(self, view: views.SwitchioEnrollmentIndexView):
        assert view.enrollment_method == models.EnrollmentMethods.IN_PERSON
        assert view.form_class == forms.CardTokenizeSuccessForm
        assert view.route_enrollment_success == routes.IN_PERSON_ENROLLMENT_SUCCESS
        assert view.route_reenrollment_error == routes.IN_PERSON_ENROLLMENT_REENROLLMENT_ERROR
        assert view.route_retry == routes.IN_PERSON_ENROLLMENT_RETRY
        assert view.route_server_error == routes.IN_PERSON_SERVER_ERROR
        assert view.route_system_error == routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR
        assert view.route_tokenize_success == routes.IN_PERSON_ENROLLMENT_SWITCHIO_INDEX
        assert view.template_name == "in_person/enrollment/index_switchio.html"

    def test_get_verified_by(self, mocker, app_request, view: views.SwitchioEnrollmentIndexView):
        app_request.user = mocker.Mock(first_name="First", last_name="Last")

        assert view._get_verified_by() == "First Last"

    def test_get_context_data(self, view: views.SwitchioEnrollmentIndexView):
        context = view.get_context_data()

        assert "title" in context

    def test_get_context_data__pre_tokenize(self, view: views.SwitchioEnrollmentIndexView):
        context = view.get_context_data()

        assert context["loading_message"] == "Connecting with payment processor..."

    def test_get_context_data__post_tokenize(self, view: views.SwitchioEnrollmentIndexView, app_request):
        app_request.GET = {"state": "tokenize"}

        context = view.get_context_data()

        assert context["loading_message"] == "Registering this contactless card for reduced fares..."

    def test_get__cancel_tokenize(self, view: views.SwitchioEnrollmentIndexView, app_request):
        app_request.GET = {"error": "canceled"}

        response = view.get(app_request)

        assert response.status_code == 302
        assert response.url == reverse(routes.ADMIN_INDEX)
