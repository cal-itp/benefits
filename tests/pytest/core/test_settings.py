import pytest

from django.conf import settings


@pytest.mark.django_db
def test_admin_not_registered(client):
    response = client.get("/admin")

    assert settings.ADMIN is False
    assert response.status_code == 404
