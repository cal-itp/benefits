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


@pytest.mark.django_db
def test_PemData_str(model_PemData):
    assert str(model_PemData) == model_PemData.label


@pytest.mark.django_db
def test_PemData_data_text_secret_name(model_PemData, mock_get_secret_by_name):
    # a secret name and not remote URL, should use secret value

    data = model_PemData.data

    mock_get_secret_by_name.assert_called_once_with(model_PemData.text_secret_name)
    assert data == mock_get_secret_by_name.return_value


@pytest.mark.django_db
def test_PemData_data_remote(model_PemData, mock_requests_get_pem_data):
    # a remote URL and no secret name, should use remote value

    model_PemData.text_secret_name = None
    model_PemData.remote_url = "http://localhost/publickey"

    assert not model_PemData.text_secret_name

    data = model_PemData.data

    mock_requests_get_pem_data.assert_called_once_with(model_PemData.remote_url, timeout=settings.REQUESTS_TIMEOUT)
    assert data == mock_requests_get_pem_data.return_value.text


@pytest.mark.django_db
def test_PemData_data_text_secret_name_and_remote__uses_text_secret(
    model_PemData, mock_get_secret_by_name, mock_requests_get_pem_data
):
    # a remote URL and the secret value is not None, should use the secret value

    model_PemData.remote_url = "http://localhost/publickey"

    data = model_PemData.data

    mock_get_secret_by_name.assert_called_once_with(model_PemData.text_secret_name)
    mock_requests_get_pem_data.assert_called_once_with(model_PemData.remote_url, timeout=settings.REQUESTS_TIMEOUT)
    assert data == mock_get_secret_by_name.return_value


@pytest.mark.django_db
def test_PemData_data_text_secret_name_and_remote__uses_remote(
    model_PemData, mock_get_secret_by_name, mock_requests_get_pem_data
):
    # a remote URL and the secret value is None, should use remote value
    model_PemData.remote_url = "http://localhost/publickey"
    mock_get_secret_by_name.return_value = None

    data = model_PemData.data

    mock_get_secret_by_name.assert_called_once_with(model_PemData.text_secret_name)
    mock_requests_get_pem_data.assert_called_once_with(model_PemData.remote_url, timeout=settings.REQUESTS_TIMEOUT)
    assert data == mock_requests_get_pem_data.return_value.text
