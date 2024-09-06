from django.urls import reverse

import pytest

from benefits.routes import routes


@pytest.mark.django_db
@pytest.mark.parametrize("viewname", [routes.IN_PERSON_ELIGIBILITY, routes.IN_PERSON_ENROLLMENT])
def test_view_not_logged_in(client, viewname):
    path = reverse(viewname)

    response = client.get(path)
    assert response.status_code == 302
    assert response.url == "/admin/login/?next=" + path


# admin_client is a fixture from pytest
# https://pytest-django.readthedocs.io/en/latest/helpers.html#admin-client-django-test-client-logged-in-as-admin
@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_eligibility_logged_in(admin_client):
    path = reverse(routes.IN_PERSON_ELIGIBILITY)

    response = admin_client.get(path)
    assert response.status_code == 200
    assert response.template_name == "in_person/eligibility.html"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_confirm_post_valid_form_eligibility_verified(admin_client):

    path = reverse(routes.IN_PERSON_ELIGIBILITY)
    form_data = {"flow": 1, "verified": True}
    response = admin_client.post(path, form_data)

    assert response.status_code == 302
    assert response.url == reverse(routes.IN_PERSON_ENROLLMENT)


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_confirm_post_valid_form_eligibility_unverified(admin_client):

    path = reverse(routes.IN_PERSON_ELIGIBILITY)
    form_data = {"flow": 1, "verified": False}
    response = admin_client.post(path, form_data)

    assert response.status_code == 200
    assert response.template_name == "in_person/eligibility.html"


@pytest.mark.django_db
@pytest.mark.usefixtures("mocked_session_agency")
def test_enrollment_logged_in_get(admin_client):
    path = reverse(routes.IN_PERSON_ENROLLMENT)

    response = admin_client.get(path)
    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment.html"
    assert "forms" in response.context_data
    assert "cta_button" in response.context_data
    assert "card_tokenize_env" in response.context_data
    assert "card_tokenize_func" in response.context_data
    assert "card_tokenize_url" in response.context_data
    assert "token_field" in response.context_data
    assert "form_retry" in response.context_data
    assert "form_success" in response.context_data

    # not supporting internationalization in in_person app yet
    assert "overlay_language" not in response.context_data


def test_reenrollment_error(admin_client):
    path = reverse(routes.IN_PERSON_ENROLLMENT_REENROLLMENT_ERROR)

    response = admin_client.get(path)

    assert response.template_name == "in_person/enrollment/reenrollment_error.html"


def test_retry(admin_client):
    path = reverse(routes.IN_PERSON_ENROLLMENT_RETRY)

    response = admin_client.get(path)

    assert response.template_name == "in_person/enrollment/retry.html"


def test_system_error(admin_client):
    path = reverse(routes.IN_PERSON_ENROLLMENT_SYSTEM_ERROR)

    response = admin_client.get(path)

    assert response.template_name == "in_person/enrollment/system_error.html"


def test_server_error(admin_client):
    path = reverse(routes.IN_PERSON_GENERIC_ERROR)

    response = admin_client.get(path)

    assert response.template_name == "in_person/enrollment/server_error.html"
