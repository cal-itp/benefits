from pathlib import Path

from django.conf import settings

import pytest

from benefits.core.models import template_path, SecretNameField
import benefits.secrets


@pytest.fixture
def mock_requests_get_pem_data(mocker):
    # intercept and spy on the GET request
    return mocker.patch("benefits.core.models.common.requests.get", return_value=mocker.Mock(text="PEM text"))


@pytest.mark.django_db
@pytest.mark.parametrize(
    "input_template,expected_path",
    [
        ("error-base.html", f"{settings.BASE_DIR}/benefits/templates/error-base.html"),
        ("core/index.html", f"{settings.BASE_DIR}/benefits/core/templates/core/index.html"),
        ("eligibility/start.html", f"{settings.BASE_DIR}/benefits/eligibility/templates/eligibility/start.html"),
        ("", None),
        ("nope.html", None),
        ("core/not-there.html", None),
    ],
)
def test_template_path(input_template, expected_path):
    if expected_path:
        assert template_path(input_template) == Path(expected_path)
    else:
        assert template_path(input_template) is None


def test_SecretNameField_init():
    field = SecretNameField()

    assert benefits.secrets.NAME_VALIDATOR in field.validators
    assert field.max_length == 127
    assert field.blank is False
    assert field.null is False
    assert field.allow_unicode is False
    assert field.description is not None
    assert field.description != ""


def test_SecretNameField_init_null_blank():
    field = SecretNameField(blank=True, null=True)

    assert field.blank is True
    assert field.null is True


def test_SecretNameField_secret_value(mocker, mock_get_secret_by_name):
    # Create a mock model instance
    mock_instance = mocker.Mock()
    mock_instance.test_field = "test-secret-name"

    # Set the field's attname to simulate how Django would set it
    field = SecretNameField()
    field.attname = "test_field"

    result = field.secret_value(mock_instance)

    # Verify the secret was retrieved with correct name
    mock_get_secret_by_name.assert_called_once_with("test-secret-name")
    assert result == mock_get_secret_by_name.return_value


@pytest.mark.django_db
def test_PemData_str(model_PemData):
    assert str(model_PemData) == model_PemData.label


@pytest.mark.django_db
def test_PemData_data_text_secret_name(mock_field_secret_value, model_PemData, mock_requests_get_pem_data):
    # a secret name and no remote URL, should use secret value

    model_PemData.remote_url = None
    mock_field = mock_field_secret_value(model_PemData, "text_secret_name")

    assert model_PemData.data == mock_field.secret_value.return_value
    mock_requests_get_pem_data.assert_not_called()


@pytest.mark.django_db
def test_PemData_data_remote(model_PemData, mock_requests_get_pem_data):
    # a remote URL and no secret name, should use remote value

    model_PemData.text_secret_name = None
    model_PemData.remote_url = "http://localhost/publickey"

    data = model_PemData.data

    mock_requests_get_pem_data.assert_called_once_with(model_PemData.remote_url, timeout=settings.REQUESTS_TIMEOUT)
    assert data == mock_requests_get_pem_data.return_value.text


@pytest.mark.django_db
def test_PemData_data_text_secret_name_and_remote__uses_text_secret(
    mock_field_secret_value, model_PemData, mock_requests_get_pem_data
):
    # a remote URL and the secret value is not None, should use the secret value
    mock_field = mock_field_secret_value(model_PemData, "text_secret_name")
    model_PemData.remote_url = "http://localhost/publickey"

    assert model_PemData.data == mock_field.secret_value.return_value
    mock_requests_get_pem_data.assert_not_called()


@pytest.mark.django_db
def test_PemData_data_text_secret_name_and_remote__uses_remote(
    model_PemData, mock_field_secret_value, mock_requests_get_pem_data
):
    # a remote URL and the secret value is None, should use remote value
    model_PemData.remote_url = "http://localhost/publickey"

    mock_field = mock_field_secret_value(model_PemData, "text_secret_name")
    mock_field.secret_value.return_value = None

    data = model_PemData.data

    mock_requests_get_pem_data.assert_called_once_with(model_PemData.remote_url, timeout=settings.REQUESTS_TIMEOUT)
    assert data == mock_requests_get_pem_data.return_value.text
