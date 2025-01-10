import pytest


@pytest.mark.django_db
def test_model_ClaimsProvider(model_ClaimsProvider):
    assert model_ClaimsProvider.supports_sign_out
    assert str(model_ClaimsProvider) == model_ClaimsProvider.client_name


@pytest.mark.django_db
def test_model_ClaimsProvider_client_id(mock_secret_name_field, secret_value, model_ClaimsProvider):
    mock_field = mock_secret_name_field(model_ClaimsProvider)

    assert model_ClaimsProvider.client_id == secret_value
    mock_field.secret_value.assert_called_once_with(model_ClaimsProvider)


@pytest.mark.django_db
def test_model_ClaimsProvider_no_sign_out(model_ClaimsProvider_no_sign_out):
    assert not model_ClaimsProvider_no_sign_out.supports_sign_out
