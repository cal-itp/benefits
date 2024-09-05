from enum import Enum
from datetime import timedelta

from django.utils import timezone
from littlepay.api.client import Client
from requests.exceptions import HTTPError
import sentry_sdk

from benefits.core import session
from . import analytics


class Status(Enum):
    # SUCCESS means the enrollment went through successfully
    SUCCESS = 1

    # SYSTEM_ERROR means the enrollment system encountered an internal error (returned a 500 HTTP status)
    SYSTEM_ERROR = 2

    # EXCEPTION means the enrollment system is working, but something unexpected happened
    # because of a misconfiguration or invalid request from our side
    EXCEPTION = 3

    # REENROLLMENT_ERROR means that the user tried to re-enroll but is not within the reenrollment window
    REENROLLMENT_ERROR = 4


def enroll(request, agency, flow, card_token):
    client = Client(
        base_url=agency.transit_processor.api_base_url,
        client_id=agency.transit_processor_client_id,
        client_secret=agency.transit_processor_client_secret,
        audience=agency.transit_processor_audience,
    )
    client.oauth.ensure_active_token(client.token)

    funding_source = client.get_funding_source_by_token(card_token)
    group_id = flow.group_id

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
            analytics.returned_error(request, str(e))
            sentry_sdk.capture_exception(e)

            status = Status.SYSTEM_ERROR
        else:
            analytics.returned_error(request, str(e))
            status = Status.EXCEPTION
            exception = Exception(f"{e}: {e.response.json()}")
    except Exception as e:
        analytics.returned_error(request, str(e))
        status = Status.EXCEPTION
        exception = e

    return status, exception


def _get_group_funding_source(client: Client, group_id, funding_source_id):
    group_funding_sources = client.get_concession_group_linked_funding_sources(group_id)
    matching_group_funding_source = None
    for group_funding_source in group_funding_sources:
        if group_funding_source.id == funding_source_id:
            matching_group_funding_source = group_funding_source
            break

    return matching_group_funding_source


def _is_expired(expiry_date):
    """Returns whether the passed in datetime is expired or not."""
    return expiry_date <= timezone.now()


def _is_within_reenrollment_window(expiry_date, enrollment_reenrollment_date):
    """Returns if we are currently within the reenrollment window."""
    return enrollment_reenrollment_date <= timezone.now() < expiry_date


def _calculate_expiry(expiration_days):
    """Returns the expiry datetime, which should be midnight in our configured timezone of the (N + 1)th day from now,
    where N is expiration_days."""
    default_time_zone = timezone.get_default_timezone()
    expiry_date = timezone.localtime(timezone=default_time_zone) + timedelta(days=expiration_days + 1)
    expiry_datetime = expiry_date.replace(hour=0, minute=0, second=0, microsecond=0)

    return expiry_datetime
