import pytest


@pytest.fixture
def secret_value():
    return "secret!"


@pytest.fixture
def mock_secret_name_field(mocker, secret_value):
    def _mock_secret_name_field(model):
        mock_meta = mocker.patch.object(model, "_meta")
        mock_field = mock_meta.get_field.return_value
        mock_field.secret_value.return_value = secret_value
        return mock_field

    return _mock_secret_name_field
