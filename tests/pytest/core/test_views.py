import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_homepage(client):
    homepage = reverse("core:index")
    response = client.get(homepage)
    assert response.status_code == 200
    assert "transit" in str(response.content)
