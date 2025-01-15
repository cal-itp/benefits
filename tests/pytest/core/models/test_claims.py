import pytest


@pytest.mark.django_db
def test_model_ClaimsProvider(model_ClaimsProvider):
    assert model_ClaimsProvider.supports_sign_out
    assert str(model_ClaimsProvider) == model_ClaimsProvider.client_name


@pytest.mark.django_db
def test_model_ClaimsProvider_client_id(mock_field_secret_value, model_ClaimsProvider):
    mock_field = mock_field_secret_value(model_ClaimsProvider, "client_id_secret_name")

    assert model_ClaimsProvider.client_id == mock_field.secret_value.return_value


@pytest.mark.django_db
def test_model_ClaimsProvider_no_sign_out(model_ClaimsProvider_no_sign_out):
    assert not model_ClaimsProvider_no_sign_out.supports_sign_out
