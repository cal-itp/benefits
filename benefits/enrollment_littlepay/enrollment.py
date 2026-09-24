import re
from dataclasses import dataclass

from littlepay.api.client import Client
from littlepay.api.funding_sources import FundingSourceResponse
from requests.exceptions import HTTPError

from benefits.core import session
from benefits.enrollment.enrollment import Status, resolve_enrollment_decision


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
        littlepay_config = agency.transit_processor
        client = Client(
            base_url=littlepay_config.api_base_url,
            client_id=littlepay_config.client_id,
            client_secret=littlepay_config.client_secret,
            audience=littlepay_config.audience,
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


def enroll(request, card_token) -> tuple[Status, Exception, FundingSourceResponse]:
    """
    Attempts to enroll this card into the transit processor group for the flow in the request's session.

    Returns a tuple containing a Status indicating the result of the attempt and any exception that occurred.
    """
    agency = session.agency(request)
    flow = session.flow(request)

    littlepay_config = agency.transit_processor
    client = Client(
        base_url=littlepay_config.api_base_url,
        client_id=littlepay_config.client_id,
        client_secret=littlepay_config.client_secret,
        audience=littlepay_config.audience,
    )
    client.oauth.ensure_active_token(client.token)

    funding_source = client.get_funding_source_by_token(card_token)
    group_id = str(session.group(request).group_id)  # needs to be a string for the API call

    exception = None
    try:
        group_funding_source = _get_group_funding_source(client=client, group_id=group_id, funding_source_id=funding_source.id)
        already_enrolled = group_funding_source is not None
        existing_expiry = group_funding_source.expiry_date if already_enrolled else None

        decision = resolve_enrollment_decision(flow, already_enrolled, existing_expiry)
        status = decision.status

        if decision.expiry_to_store is not None:
            session.update(request, enrollment_expiry=decision.expiry_to_store)

        if status is Status.SUCCESS:
            if decision.should_remove_expiry:
                raise NotImplementedError("Removing expiration date is currently not supported")
            elif decision.should_enroll:
                if not already_enrolled:
                    if decision.expiry_to_send is None:
                        client.link_concession_group_funding_source(group_id=group_id, funding_source_id=funding_source.id)
                    else:
                        client.link_concession_group_funding_source(
                            group_id=group_id, funding_source_id=funding_source.id, expiry=decision.expiry_to_send
                        )
                else:
                    client.update_concession_group_funding_source_expiry(
                        group_id=group_id, funding_source_id=funding_source.id, expiry=decision.expiry_to_send
                    )

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
