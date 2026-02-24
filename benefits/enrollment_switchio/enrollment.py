from dataclasses import dataclass
from datetime import datetime

from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse
from requests import HTTPError

from benefits.core import session
from benefits.core.models.enrollment import EnrollmentFlow
from benefits.enrollment.enrollment import Status, _calculate_expiry, _is_expired, _is_within_reenrollment_window
from benefits.enrollment_switchio.api import (
    EnrollmentClient,
    EshopResponseMode,
    Registration,
    RegistrationMode,
    RegistrationStatus,
    TokenizationClient,
)
from benefits.enrollment_switchio.models import SwitchioConfig
from benefits.routes import routes


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


def request_registration(
    request, switchio_config: SwitchioConfig, redirect_route: str = routes.ENROLLMENT_SWITCHIO_INDEX
) -> RegistrationResponse:
    try:
        client = TokenizationClient(
            api_url=switchio_config.tokenization_api_base_url,
            api_key=switchio_config.tokenization_api_key,
            api_secret=switchio_config.tokenization_api_secret,
            private_key=switchio_config.private_key_data,
            client_certificate=switchio_config.client_certificate_data,
            ca_certificate=switchio_config.ca_certificate_data,
        )

        route = reverse(redirect_route)
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


def enroll(request, switchio_config: SwitchioConfig, flow: EnrollmentFlow, token: str) -> tuple[Status, Exception]:
    client = EnrollmentClient(
        api_url=switchio_config.enrollment_api_base_url,
        authorization_header_value=switchio_config.enrollment_api_authorization_header,
        private_key=switchio_config.private_key_data,
        client_certificate=switchio_config.client_certificate_data,
        ca_certificate=switchio_config.ca_certificate_data,
    )

    pto_id = switchio_config.pto_id
    group_id = flow.group_id

    exception = None
    try:
        group = _get_group_for_token(client, pto_id, group_id, token)
        already_enrolled = group is not None

        if flow.supports_expiration:
            # set expiry on session
            if already_enrolled and group.expiresAt is not None:
                session.update(request, enrollment_expiry=group.expiresAt)
            else:
                session.update(request, enrollment_expiry=_calculate_expiry(flow.expiration_days))

            if not already_enrolled:
                # enroll user with an expiration date, return success
                client.add_group_to_token(pto_id, group_id, token, expiry=session.enrollment_expiry(request))
                status = Status.SUCCESS
            else:  # already_enrolled
                if group.expiresAt is None:
                    # update expiration of existing enrollment, return success
                    client.add_group_to_token(pto_id, group_id, token, expiry=session.enrollment_expiry(request))
                    status = Status.SUCCESS
                else:
                    is_expired = _is_expired(group.expiresAt)
                    is_within_reenrollment_window = _is_within_reenrollment_window(
                        group.expiresAt, session.enrollment_reenrollment(request)
                    )

                    if is_expired or is_within_reenrollment_window:
                        # update expiration of existing enrollment, return success
                        client.add_group_to_token(pto_id, group_id, token, expiry=session.enrollment_expiry(request))
                        status = Status.SUCCESS
                    else:
                        # re-enrollment error, return enrollment error with expiration and reenrollment_date
                        status = Status.REENROLLMENT_ERROR
        else:  # flow does not support expiration
            if not already_enrolled:
                # enroll user with no expiration date, return success
                client.add_group_to_token(
                    pto_id=pto_id,
                    group_id=group_id,
                    token=token,
                    timeout=settings.REQUESTS_TIMEOUT,
                )
                status = Status.SUCCESS
            else:  # already enrolled
                if group.expiresAt is None:
                    # no action, return success
                    status = Status.SUCCESS
                else:
                    # remove expiration date, return success
                    # (when you don't include an expiration date, Switchio will set the expiration date to null.)
                    client.add_group_to_token(
                        pto_id=pto_id,
                        group_id=group_id,
                        token=token,
                        timeout=settings.REQUESTS_TIMEOUT,
                    )
                    status = Status.SUCCESS
    except HTTPError as e:
        if e.response.status_code >= 500:
            status = Status.SYSTEM_ERROR
            exception = e
        else:
            status = Status.EXCEPTION
            exception = Exception(f"{e}: {e.response.text}")
    except Exception as e:
        status = Status.EXCEPTION
        exception = e

    return status, exception


def _get_group_for_token(client: EnrollmentClient, pto_id, group_id, token):
    already_enrolled_groups = client.get_groups_for_token(pto_id=pto_id, token=token, timeout=settings.REQUESTS_TIMEOUT)

    for group in already_enrolled_groups:
        if group.group == group_id:
            return group

    return None
