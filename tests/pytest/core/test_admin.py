import pytest
from django.contrib.auth.models import User
import benefits.core.admin
from benefits.core.admin import GOOGLE_USER_INFO_URL, pre_login_user, EligibilityTypeForm


@pytest.fixture
def model_AdminUser():
    return User.objects.create(email="user@calitp.org", first_name="", last_name="", username="")


@pytest.mark.django_db
def test_admin_registered(client):
    response = client.get("/admin", follow=True)

    assert response.status_code == 200
    assert ("/admin/", 301) in response.redirect_chain
    assert ("/admin/login/?next=/admin/", 302) in response.redirect_chain
    assert response.request["PATH_INFO"] == "/admin/login/"
    assert "google_sso/login.html" in response.template_name


@pytest.mark.django_db
def test_pre_login_user(mocker, model_AdminUser):
    assert model_AdminUser.email == "user@calitp.org"
    assert model_AdminUser.first_name == ""
    assert model_AdminUser.last_name == ""
    assert model_AdminUser.username == ""

    response_from_google = {
        "username": "admin@calitp.org",
        "given_name": "Admin",
        "family_name": "User",
        "email": "admin@calitp.org",
    }

    mocked_request = mocker.Mock()
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = response_from_google
    requests_spy = mocker.patch("benefits.core.admin.requests.get", return_value=mocked_response)

    pre_login_user(model_AdminUser, mocked_request)

    requests_spy.assert_called_once()
    assert GOOGLE_USER_INFO_URL in requests_spy.call_args.args
    assert model_AdminUser.email == response_from_google["email"]
    assert model_AdminUser.first_name == response_from_google["given_name"]
    assert model_AdminUser.last_name == response_from_google["family_name"]
    assert model_AdminUser.username == response_from_google["username"]


@pytest.mark.django_db
def test_pre_login_user_no_session_token(mocker, model_AdminUser):
    mocked_request = mocker.Mock()
    mocked_request.session.get.return_value = None
    logger_spy = mocker.spy(benefits.core.admin, "logger")

    pre_login_user(model_AdminUser, mocked_request)

    assert model_AdminUser.email == "user@calitp.org"
    assert model_AdminUser.first_name == ""
    assert model_AdminUser.last_name == ""
    assert model_AdminUser.username == ""
    logger_spy.warning.assert_called_once()


def eligibility_type_form_data(supports_expiration=False, expiration_days=None, expiration_reenrollment_days=None):
    form_data = {
        "name": "calfresh",
        "label": "CalFresh recipients",
        "group_id": "123",
        "supports_expiration": supports_expiration,
    }

    if expiration_days:
        form_data.update(expiration_days=expiration_days)

    if expiration_reenrollment_days:
        form_data.update(expiration_reenrollment_days=expiration_reenrollment_days)

    return form_data


@pytest.mark.django_db
def test_EligibilityTypeForm_supports_expiration_False():
    form_data = eligibility_type_form_data(supports_expiration=False)
    form = EligibilityTypeForm(form_data)
    assert form.is_valid()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "valid_expiration_reenrollment_days",
    ["1", "14", "30"],
    ids=lambda n: f"negative expiration_days, valid expiration_enrollment_days ({n})",
)
def test_EligibilityTypeForm_supports_expiration_True_negative_expiration_days(valid_expiration_reenrollment_days):
    form_data = eligibility_type_form_data(
        supports_expiration=True, expiration_days=-20, expiration_reenrollment_days=valid_expiration_reenrollment_days
    )
    form = EligibilityTypeForm(form_data)

    # assert state of the form
    assert not form.is_valid()
    assert len(form.errors) == 1

    # assert state of specific field
    errors = form.errors["expiration_days"]
    assert len(errors) == 2

    # error message coming from PositiveSmallIntegerField validation
    assert errors[0] == "Ensure this value is greater than or equal to 0."
    # our custom validation message for when supports_expiration is True
    assert errors[1] == "When support_expiration is True, this value must be greater than 0."


@pytest.mark.django_db
@pytest.mark.parametrize(
    "valid_expiration_reenrollment_days",
    ["1", "14", "30"],
    ids=lambda n: f"zero expiration days, valid expiration_enrollment_days ({n})",
)
def test_EligibilityTypeForm_supports_expiration_True_zero_expiration_days(valid_expiration_reenrollment_days):
    form_data = eligibility_type_form_data(
        supports_expiration=True, expiration_days=0, expiration_reenrollment_days=valid_expiration_reenrollment_days
    )
    form = EligibilityTypeForm(form_data)

    # assert state of the form
    assert not form.is_valid()
    assert len(form.errors) == 1

    # assert state of specific field
    errors = form.errors["expiration_days"]
    assert len(errors) == 1

    # our custom validation message for when supports_expiration is True
    assert errors[0] == "When support_expiration is True, this value must be greater than 0."


@pytest.mark.django_db
@pytest.mark.parametrize(
    "valid_expiration_days",
    ["1", "14", "30"],
    ids=lambda n: f"valid expiration_days ({n}), negative expiration_reenrollment_days",
)
def test_EligibilityTypeForm_supports_expiration_True_negative_expiration_reenrollment_days(valid_expiration_days):
    form_data = eligibility_type_form_data(
        supports_expiration=True, expiration_days=valid_expiration_days, expiration_reenrollment_days=-20
    )
    form = EligibilityTypeForm(form_data)

    # assert state of the form
    assert not form.is_valid()
    assert len(form.errors) == 1

    # assert state of specific field
    errors = form.errors["expiration_reenrollment_days"]
    assert len(errors) == 2

    # error message coming from PositiveSmallIntegerField validation
    assert errors[0] == "Ensure this value is greater than or equal to 0."
    # our custom validation message for when supports_expiration is True
    assert errors[1] == "When support_expiration is True, this value must be greater than 0."


@pytest.mark.django_db
@pytest.mark.parametrize(
    "valid_expiration_days",
    ["1", "14", "30"],
    ids=lambda n: f"valid expiration_days ({n}), zero expiration_reenrollment_days",
)
def test_EligibilityTypeForm_supports_expiration_True_zero_expiration_reenrollment_days(valid_expiration_days):
    form_data = eligibility_type_form_data(
        supports_expiration=True, expiration_days=valid_expiration_days, expiration_reenrollment_days=0
    )
    form = EligibilityTypeForm(form_data)

    # assert state of the form
    assert not form.is_valid()
    assert len(form.errors) == 1

    # assert state of specific field
    errors = form.errors["expiration_reenrollment_days"]
    assert len(errors) == 1

    # our custom validation message for when supports_expiration is True
    assert errors[0] == "When support_expiration is True, this value must be greater than 0."
