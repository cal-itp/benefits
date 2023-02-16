from django.test import Client
from django.urls import reverse

import pytest

from benefits.core import session
from benefits.core.models import TransitAgency
from benefits.core.views import ROUTE_INDEX, TEMPLATE_PAGE


@pytest.mark.django_db
@pytest.mark.parametrize("user_agent", ["AlwaysOn", "Edge Health Probe"])
def test_healthcheck_user_agent(mocker, user_agent):
    mocker.patch.object(session.settings, "HEALTHCHECK_USER_AGENTS", [user_agent])
    client = Client(HTTP_USER_AGENT=user_agent)

    response = client.get(reverse(ROUTE_INDEX))

    assert response.status_code == 200
    assert response.content.decode("UTF-8") == "Healthy"


@pytest.mark.django_db
def test_non_healthcheck_user_agent(mocker, model_TransitAgency, client):
    # create another Transit Agency by cloning the original to ensure there are multiple
    # https://stackoverflow.com/a/48149675/453168
    new_agency = TransitAgency.objects.get(pk=model_TransitAgency.id)
    new_agency.pk = None
    new_agency.save()

    mocker.patch.object(session.settings, "HEALTHCHECK_USER_AGENTS", ["AlwaysOn"])

    response = client.get(reverse(ROUTE_INDEX))

    assert response.status_code == 200
    assert response.template_name == TEMPLATE_PAGE
