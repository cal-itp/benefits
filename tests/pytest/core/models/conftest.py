import pytest


@pytest.fixture
def secret_value():
    return "secret!"


@pytest.fixture
def mock_field_secret_value(mocker, secret_value):
    def _mock_field_secret_value(model, field_name):
        field = model._meta.get_field(field_name)
        mock = mocker.patch.object(field, "secret_value")
        mock.return_value = secret_value
        return field

    return _mock_field_secret_value
