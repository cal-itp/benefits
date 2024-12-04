from playwright.sync_api import Page, expect
import pytest


@pytest.fixture
def env_base_url(request):
    marker = (
        request.node.get_closest_marker("dev")
        or request.node.get_closest_marker("test")
        or request.node.get_closest_marker("prod")
    )
    print(marker)

    if marker:
        env = marker.name
    else:
        env = None

    if env == "dev":
        return "https://dev-benefits.calitp.org"
    elif env == "test":
        return "https://test-benefits.calitp.org"
    elif env == "prod":
        return "http://dev-benefits.calitp.org"  # use dev for now, don't want to spam prod
    else:
        return "http://localhost:11369"  # use port that will work with IdG


def env(*marks):
    return pytest.mark.parametrize("env_name", [pytest.param(mark.name, marks=mark) for mark in marks])


@env(pytest.mark.dev, pytest.mark.test, pytest.mark.prod)
def test_healthcheck(page: Page, env_base_url, env_name):
    page.goto(env_base_url + "/healthcheck")

    expect(page.get_by_text("Healthy")).to_be_visible()
