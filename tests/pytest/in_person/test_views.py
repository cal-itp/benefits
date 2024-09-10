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


def test_enrollment_logged_in(admin_client):
    path = reverse(routes.IN_PERSON_ENROLLMENT)

    response = admin_client.get(path)
    assert response.status_code == 200
    assert response.template_name == "in_person/enrollment.html"


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
