import pytest

from benefits.routes import routes


@pytest.mark.parametrize(("route", "expected_name"), [("app:name", "name"), ("core:index", "index")])
def test_name_route(route: str, expected_name: str):
    assert routes.name(route) == expected_name


@pytest.mark.parametrize(("route"), ["app", "core"])
def test_name_not_route(route: str):
    assert routes.name(route) == route
