import pytest
from django.urls import reverse


from benefits.core import models
from benefits.enrollment.enrollment import Status
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
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "model_LittlepayConfig")
def test_enrollment_logged_in_get(admin_client):
    path = reverse(routes.IN_PERSON_ENROLLMENT_LITTLEPAY_INDEX)

    response = admin_client.get(path)
    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment/index.html"
    assert "forms" in response.context_data
    assert "cta_button" in response.context_data
    assert "token_field" in response.context_data
    assert "form_retry" in response.context_data
    assert "form_success" in response.context_data
    assert "card_types" in response.context_data

    # not supporting internationalization in in_person app yet
    assert "overlay_language" not in response.context_data


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "mocked_session_eligible")
def test_enrollment_post_invalid_form(admin_client, invalid_form_data):
    path = reverse(routes.IN_PERSON_ENROLLMENT_LITTLEPAY_INDEX)

    with pytest.raises(Exception, match=r"form"):
        admin_client.post(path, invalid_form_data)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "model_EnrollmentFlow", "model_LittlepayGroup")
def test_enrollment_post_valid_form_success(
    mocker,
    admin_client,
    card_tokenize_form_data,
    mocked_eligibility_analytics_module,
    mocked_enrollment_analytics_module,
    model_TransitAgency,
    model_EnrollmentFlow,
    model_User,
):
    mocker.patch("benefits.in_person.views.enroll", return_value=(Status.SUCCESS, None))
    spy = mocker.spy(views.models.EnrollmentEvent.objects, "create")

    # force the model_User to be the logged in user
    # e.g. the TransitAgency staff person assisting this in-person enrollment
    admin_client.force_login(model_User)

    path = reverse(routes.IN_PERSON_ENROLLMENT_LITTLEPAY_INDEX)
    response = admin_client.post(path, card_tokenize_form_data)

    spy.assert_called_once_with(
        transit_agency=model_TransitAgency,
        enrollment_flow=model_EnrollmentFlow,
        enrollment_method=models.EnrollmentMethods.IN_PERSON,
        verified_by=f"{model_User.first_name} {model_User.last_name}",
        expiration_datetime=None,
    )

    assert response.status_code == 302
    assert response.url == reverse(routes.IN_PERSON_ENROLLMENT_SUCCESS)
    mocked_enrollment_analytics_module.returned_success.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "model_EnrollmentFlow")
def test_enrollment_post_valid_form_system_error(
    mocker, admin_client, card_tokenize_form_data, mocked_enrollment_analytics_module, mocked_sentry_sdk_module
):
    mocker.patch("benefits.in_person.views.enroll", return_value=(Status.SYSTEM_ERROR, None))

    path = reverse(routes.IN_PERSON_ENROLLMENT_LITTLEPAY_INDEX)
    response = admin_client.post(path, card_tokenize_form_data)

    assert response.status_code == 302
    assert response.url == reverse(routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR)
    mocked_enrollment_analytics_module.returned_error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "model_EnrollmentFlow")
def test_enrollment_post_valid_form_exception(
    mocker, admin_client, card_tokenize_form_data, mocked_enrollment_analytics_module, mocked_sentry_sdk_module
):
    mocker.patch("benefits.in_person.views.enroll", return_value=(Status.EXCEPTION, None))

    path = reverse(routes.IN_PERSON_ENROLLMENT_LITTLEPAY_INDEX)
    response = admin_client.post(path, card_tokenize_form_data)

    assert response.status_code == 302
    assert response.url == reverse(routes.IN_PERSON_SERVER_ERROR)
    mocked_enrollment_analytics_module.returned_error.assert_called_once()
    mocked_sentry_sdk_module.capture_exception.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency", "mocked_session_flow", "model_EnrollmentFlow")
def test_enrollment_post_valid_form_reenrollment_error(
    mocker, admin_client, card_tokenize_form_data, mocked_enrollment_analytics_module
):
    mocker.patch("benefits.in_person.views.enroll", return_value=(Status.REENROLLMENT_ERROR, None))

    path = reverse(routes.IN_PERSON_ENROLLMENT_LITTLEPAY_INDEX)
    response = admin_client.post(path, card_tokenize_form_data)

    assert response.status_code == 302
    assert response.url == reverse(routes.IN_PERSON_ENROLLMENT_REENROLLMENT_ERROR)
    mocked_enrollment_analytics_module.returned_error.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow", "mocked_session_agency")
def test_reenrollment_error(admin_client):
    path = reverse(routes.IN_PERSON_ENROLLMENT_REENROLLMENT_ERROR)

    response = admin_client.get(path)

    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment/reenrollment_error.html"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow", "mocked_session_agency")
def test_retry(admin_client, mocked_enrollment_analytics_module):
    path = reverse(routes.IN_PERSON_ENROLLMENT_RETRY)

    response = admin_client.get(path)

    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment/retry.html"
    mocked_enrollment_analytics_module.returned_retry.assert_not_called()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow", "mocked_session_agency")
def test_retry_post(admin_client, mocked_enrollment_analytics_module):
    path = reverse(routes.IN_PERSON_ENROLLMENT_RETRY)

    response = admin_client.post(path)

    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment/retry.html"
    mocked_enrollment_analytics_module.returned_retry.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow", "mocked_session_agency")
def test_system_error(admin_client):
    path = reverse(routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR)

    response = admin_client.get(path)

    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment/system_error.html"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_flow", "mocked_session_agency")
def test_server_error(admin_client):
    path = reverse(routes.IN_PERSON_SERVER_ERROR)

    response = admin_client.get(path)

    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment/server_error.html"


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
        assert view.route_system_error == routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR
        assert view.route_server_error == routes.IN_PERSON_SERVER_ERROR
