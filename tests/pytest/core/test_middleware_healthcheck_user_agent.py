from django.test import Client
from django.urls import reverse

import pytest

from benefits.routes import routes
from benefits.core import middleware
from benefits.core.views import TEMPLATE_INDEX


@pytest.mark.django_db
@pytest.mark.parametrize("user_agent", ["AlwaysOn", "Edge Health Probe"])
def test_healthcheck_user_agent(mocker, user_agent):
    mocker.patch.object(middleware.settings, "HEALTHCHECK_USER_AGENTS", [user_agent])
    client = Client(HTTP_USER_AGENT=user_agent)

    response = client.get(reverse(routes.INDEX))

    assert response.status_code == 200
    assert response.content.decode("UTF-8") == "Healthy"


@pytest.mark.django_db
def test_non_healthcheck_user_agent(mocker, client):
    mocker.patch.object(middleware.settings, "HEALTHCHECK_USER_AGENTS", ["AlwaysOn"])

    response = client.get(reverse(routes.INDEX))

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_INDEX
