import pytest

from benefits.routes import Routes, routes


@pytest.mark.parametrize(("route", "expected_name"), [("app:name", "name"), ("core:index", "index")])
def test_name_route(route: str, expected_name: str):
    assert routes.name(route) == expected_name


@pytest.mark.parametrize(("route"), ["app", "core"])
def test_name_not_route(route: str):
    assert routes.name(route) == route


def test_to_dict():
    routes_dict = routes.to_dict()

    # this is in fact, a dict!
    assert isinstance(routes_dict, dict)
    # all keys are strings
    assert all((isinstance(k, str) for k in routes_dict.keys()))
    # all keys are @property on the original routes object
    assert all((hasattr(routes, k) and isinstance(getattr(Routes, k), property) for k in routes_dict.keys()))
    # all key values equal their corresponding attribute value
    assert all((routes_dict[k] == getattr(routes, k)) for k in routes_dict.keys())
