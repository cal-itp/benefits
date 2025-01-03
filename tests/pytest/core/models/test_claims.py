import pytest


@pytest.mark.django_db
def test_model_ClaimsProvider(model_ClaimsProvider):
    assert model_ClaimsProvider.supports_sign_out
    assert str(model_ClaimsProvider) == model_ClaimsProvider.client_name


@pytest.mark.django_db
def test_model_ClaimsProvider_client_id(model_ClaimsProvider, mock_get_secret_by_name):
    secret_value = model_ClaimsProvider.client_id

    mock_get_secret_by_name.assert_called_once_with(model_ClaimsProvider.client_id_secret_name)
    assert secret_value == mock_get_secret_by_name.return_value


@pytest.mark.django_db
def test_model_ClaimsProvider_no_sign_out(model_ClaimsProvider_no_sign_out):
    assert not model_ClaimsProvider_no_sign_out.supports_sign_out
