from dataclasses import dataclass
from datetime import datetime
from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse
from requests import HTTPError

from benefits.enrollment.enrollment import Status
from benefits.enrollment_switchio.models import SwitchioConfig
from benefits.routes import routes
from benefits.enrollment_switchio.api import (
    TokenizationClient,
    EshopResponseMode,
    Registration,
    RegistrationMode,
    RegistrationStatus,
)


@dataclass
class RegistrationResponse:
    status: Status
    registration: Registration
    exception: Exception = None
    status_code: int = None


@dataclass
class RegistrationStatusResponse:
    status: Status
    registration_status: RegistrationStatus
    exception: Exception = None
    status_code: int = None


@dataclass
class Token:
    token: str
    tokenVersion: int
    tokenState: str
    validFrom: datetime
    validTo: datetime
    testOnly: bool
    par: str = None


def request_registration(request, switchio_config: SwitchioConfig) -> RegistrationResponse:
    try:
        client = TokenizationClient(
            api_url=switchio_config.tokenization_api_base_url,
            api_key=switchio_config.tokenization_api_key,
            api_secret=switchio_config.tokenization_api_secret,
            private_key=switchio_config.private_key_data,
            client_certificate=switchio_config.client_certificate_data,
            ca_certificate=switchio_config.ca_certificate_data,
        )

        route = reverse(routes.ENROLLMENT_SWITCHIO_INDEX)
        redirect_url = _generate_redirect_uri(request, route)

        registration = client.request_registration(
            eshopRedirectUrl=redirect_url,
            mode=RegistrationMode.REGISTER,
            eshopResponseMode=EshopResponseMode.QUERY,
            timeout=settings.REQUESTS_TIMEOUT,
        )

        return RegistrationResponse(status=Status.SUCCESS, registration=registration)
    except Exception as e:
        exception = e

        if isinstance(e, HTTPError):
            status_code = e.response.status_code

            if status_code >= 500:
                status = Status.SYSTEM_ERROR
            else:
                status = Status.EXCEPTION
        else:
            status_code = None
            status = Status.EXCEPTION

    return RegistrationResponse(status=status, registration=None, exception=exception, status_code=status_code)


# copied from https://github.com/Office-of-Digital-Services/django-cdt-identity/blob/main/cdt_identity/views.py#L42-L50
def _generate_redirect_uri(request: HttpRequest, redirect_path: str):
    redirect_uri = str(request.build_absolute_uri(redirect_path)).lower()

    # this is a temporary hack to ensure redirect URIs are HTTPS when the app is deployed
    # see https://github.com/cal-itp/benefits/issues/442 for more context
    if not redirect_uri.startswith("http://localhost"):
        redirect_uri = redirect_uri.replace("http://", "https://")

    return redirect_uri


def get_registration_status(switchio_config: SwitchioConfig, registration_id: str) -> RegistrationStatusResponse:
    try:
        client = TokenizationClient(
            api_url=switchio_config.tokenization_api_base_url,
            api_key=switchio_config.tokenization_api_key,
            api_secret=switchio_config.tokenization_api_secret,
            private_key=switchio_config.private_key_data,
            client_certificate=switchio_config.client_certificate_data,
            ca_certificate=switchio_config.ca_certificate_data,
        )

        registration_status = client.get_registration_status(
            registration_id=registration_id,
            timeout=settings.REQUESTS_TIMEOUT,
        )

        return RegistrationStatusResponse(status=Status.SUCCESS, registration_status=registration_status, exception=None)
    except Exception as e:
        exception = e

        if isinstance(e, HTTPError):
            status_code = e.response.status_code

            if status_code >= 500:
                status = Status.SYSTEM_ERROR
            else:
                status = Status.EXCEPTION
        else:
            status_code = None
            status = Status.EXCEPTION

        return RegistrationStatusResponse(
            status=status, registration_status=None, exception=exception, status_code=status_code
        )


def get_latest_active_token_value(tokens):
    latest_active_token = None

    for token_dict in tokens:
        token = Token(**token_dict)
        if token.tokenState == "active":
            if latest_active_token is None or token.validFrom > latest_active_token.validFrom:
                latest_active_token = token

    return latest_active_token.token if latest_active_token else ""
