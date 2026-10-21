from requests import HTTPError

from benefits.core import session
from benefits.core.models.enrollment import EnrollmentFlow
from benefits.enrollment.enrollment import Status, resolve_enrollment_decision
from benefits.enrollment_init.models import InitConfig, InitGroup

from .api import CardholderResponse, Client, TransitAccountResponse


def enroll(request, init_config: InitConfig, flow: EnrollmentFlow, group: InitGroup, token: str):
    client = Client(
        init_config.registration_api_base_url,
        init_config.registration_api_username,
        init_config.registration_api_password,
    )

    try:
        transit_account = _get_transit_account(client, token)
        cardholder = _get_cardholder(client, transit_account)
        already_enrolled = _is_already_enrolled(cardholder, group)
        existing_expiry = cardholder.FareCategoryExpiry if already_enrolled else None

        decision = resolve_enrollment_decision(flow, already_enrolled, existing_expiry)
        status = decision.status

        if decision.expiry_to_store is not None:
            session.update(request, enrollment_expiry=decision.expiry_to_store)

        if status is Status.SUCCESS:
            if decision.should_remove_expiry:
                # put_cardholder with empty expiry
                pass
            elif decision.should_enroll:
                if not already_enrolled:
                    if decision.expiry_to_send is None:
                        # post_cardholder with no expiry
                        pass
                    else:
                        # post_cardholder with expiry_to_send
                        pass
                else:
                    # put_cardholder with expiry_to_send
                    pass
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


def _get_transit_account(client: Client, token: str):
    return client.get_transit_account(token)


def _get_cardholder(client: Client, transit_account: TransitAccountResponse):
    if transit_account and transit_account.CardholderId:
        cardholder = client.get_cardholder(transit_account.CardholderId)
    else:
        cardholder = None

    return cardholder


def _is_already_enrolled(cardholder: CardholderResponse, group: InitGroup):
    """
    A token is considered "already enrolled" with a `group` if its TransitAccount has a Cardholder whose FareCategory ID
    matches the InitGroup ID.

    Otherwise, the token will be considered as not enrolled yet and should be enrolled into the FareCategory
    for the given `group`.
    """
    if cardholder:
        return cardholder.FareCategory == group.group_id
    else:
        return False
