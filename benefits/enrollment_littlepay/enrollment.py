import re
from dataclasses import dataclass

from littlepay.api.client import Client
from requests.exceptions import HTTPError

from benefits.core import session
from benefits.enrollment.enrollment import Status, _calculate_expiry, _is_expired, _is_within_reenrollment_window


@dataclass
class CardTokenizationAccessResponse:
    status: Status
    access_token: str
    expires_at: int
    exception: Exception = None
    status_code: int = None


def request_card_tokenization_access(request) -> CardTokenizationAccessResponse:
    """
    Requests an access token to be used for card tokenization.
    """
    agency = session.agency(request)

    try:
        client = Client(
            base_url=agency.littlepay_config.api_base_url,
            client_id=agency.littlepay_config.client_id,
            client_secret=agency.littlepay_config.client_secret,
            audience=agency.littlepay_config.audience,
        )
        client.oauth.ensure_active_token(client.token)
        response = client.request_card_tokenization_access()

        return CardTokenizationAccessResponse(
            status=Status.SUCCESS, access_token=response.get("access_token"), expires_at=response.get("expires_at")
        )
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

    return CardTokenizationAccessResponse(
        status=status, access_token=None, expires_at=None, exception=exception, status_code=status_code
    )


def enroll(request, card_token) -> tuple[Status, Exception]:
    """
    Attempts to enroll this card into the transit processor group for the flow in the request's session.

    Returns a tuple containing a Status indicating the result of the attempt and any exception that occurred.
    """
    agency = session.agency(request)
    flow = session.flow(request)

    client = Client(
        base_url=agency.littlepay_config.api_base_url,
        client_id=agency.littlepay_config.client_id,
        client_secret=agency.littlepay_config.client_secret,
        audience=agency.littlepay_config.audience,
    )
    client.oauth.ensure_active_token(client.token)

    funding_source = client.get_funding_source_by_token(card_token)
    group_id = str(session.group(request).group_id)  # needs to be a string for the API call

    exception = None
    try:
        group_funding_source = _get_group_funding_source(client=client, group_id=group_id, funding_source_id=funding_source.id)

        already_enrolled = group_funding_source is not None

        if flow.supports_expiration:
            # set expiry on session
            if already_enrolled and group_funding_source.expiry_date is not None:
                session.update(request, enrollment_expiry=group_funding_source.expiry_date)
            else:
                session.update(request, enrollment_expiry=_calculate_expiry(flow.expiration_days))

            if not already_enrolled:
                # enroll user with an expiration date, return success
                client.link_concession_group_funding_source(
                    group_id=group_id, funding_source_id=funding_source.id, expiry=session.enrollment_expiry(request)
                )
                status = Status.SUCCESS
            else:  # already_enrolled
                if group_funding_source.expiry_date is None:
                    # update expiration of existing enrollment, return success
                    client.update_concession_group_funding_source_expiry(
                        group_id=group_id,
                        funding_source_id=funding_source.id,
                        expiry=session.enrollment_expiry(request),
                    )
                    status = Status.SUCCESS
                else:
                    is_expired = _is_expired(group_funding_source.expiry_date)
                    is_within_reenrollment_window = _is_within_reenrollment_window(
                        group_funding_source.expiry_date, session.enrollment_reenrollment(request)
                    )

                    if is_expired or is_within_reenrollment_window:
                        # update expiration of existing enrollment, return success
                        client.update_concession_group_funding_source_expiry(
                            group_id=group_id,
                            funding_source_id=funding_source.id,
                            expiry=session.enrollment_expiry(request),
                        )
                        status = Status.SUCCESS
                    else:
                        # re-enrollment error, return enrollment error with expiration and reenrollment_date
                        status = Status.REENROLLMENT_ERROR
        else:  # eligibility does not support expiration
            if not already_enrolled:
                # enroll user with no expiration date, return success
                client.link_concession_group_funding_source(group_id=group_id, funding_source_id=funding_source.id)
                status = Status.SUCCESS
            else:  # already_enrolled
                if group_funding_source.expiry_date is None:
                    # no action, return success
                    status = Status.SUCCESS
                else:
                    # remove expiration date, return success
                    raise NotImplementedError("Removing expiration date is currently not supported")

    except HTTPError as e:
        if e.response.status_code >= 500:
            status = Status.SYSTEM_ERROR
            exception = e
        elif e.response.status_code == 409 and re.search(r"Funding source .+ already in group", e.response.text):
            # Handle situations where we errantly tried to link an already-enrolled funding source.
            # See: https://github.com/cal-itp/benefits/issues/3292
            status = Status.SUCCESS
        else:
            status = Status.EXCEPTION
            exception = Exception(f"{e}: {e.response.json()}")
    except Exception as e:
        status = Status.EXCEPTION
        exception = e

    return status, exception, funding_source


def _get_group_funding_source(client: Client, group_id, funding_source_id):
    group_funding_sources = client.get_concession_group_linked_funding_sources(group_id)
    matching_group_funding_source = None
    for group_funding_source in group_funding_sources:
        if group_funding_source.id == funding_source_id:
            matching_group_funding_source = group_funding_source
            break

    return matching_group_funding_source
