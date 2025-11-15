import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_benefits_password_reset_view_success_url(client):
    form_path = reverse("admin_password_reset")
    done_path = reverse("password_reset_done")
    email = "mail@example.com"
    response = client.post(form_path, {"email": email})

    assert response.status_code == 302
    assert response.url == f"{done_path}?email={email}"


@pytest.mark.django_db
def test_benefits_password_reset_done_view_context(client):
    form_path = reverse("admin_password_reset")
    email = "mail@example.com"
    response = client.post(form_path, {"email": email}, follow=True)
    # breakpoint()
    assert response.context["email"] == email
