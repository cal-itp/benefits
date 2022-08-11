from benefits.core.middleware import HEALTHCHECK_PATH


def test_healthcheck(client):
    response = client.get(HEALTHCHECK_PATH)
    assert response.status_code == 200
