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


# region --- Test that needs to run for multiple environments


# region helper function
def env(*marks):
    return pytest.mark.parametrize("env_name", [pytest.param(mark.name, marks=mark) for mark in marks])


# endregion


# this is what the helper function evaluates to
# @pytest.mark.parametrize(
#     "env_name",
#     [
#         pytest.param("dev", marks=[pytest.mark.dev]),
#         pytest.param("test", marks=[pytest.mark.test]),
#         pytest.param("prod", marks=[pytest.mark.prod]),
#     ],
# )
@env(pytest.mark.dev, pytest.mark.test, pytest.mark.prod)
def test_healthcheck(page: Page, env_base_url, env_name):
    page.goto(env_base_url + "/healthcheck")

    expect(page.get_by_text("Healthy")).to_be_visible()


# endregion


# region--- Test that needs to run for multiple environments with parametrized values


@pytest.mark.parametrize(
    "sub,name",
    [
        pytest.param("12345", "Example", marks=[pytest.mark.dev]),
        pytest.param("1234", "Le", marks=[pytest.mark.dev]),
        pytest.param("4321", "Garcia", marks=[pytest.mark.test]),
        pytest.param("54321", "Sample", marks=[pytest.mark.prod]),
    ],
)
def test_agency_card_flow(page, env_base_url, sub, name):
    print(env_base_url)
    print(sub)
    print(name)


# endregion


# region --- Test specific to only one environment that does not need parameterization, can use mark more simply


@pytest.mark.dev
def test_only_for_dev(env_base_url):
    print(env_base_url)


# endregion
