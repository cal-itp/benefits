import pytest


@pytest.mark.django_db
def test_admin_registered(client):
    response = client.get("/admin")

    assert response.status_code == 301
