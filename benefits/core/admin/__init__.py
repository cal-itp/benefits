"""
The core application: Admin interface configuration.
"""

from .common import PemDataAdmin
from .claims import ClaimsProviderAdmin
from .transit import TransitAgencyAdmin, TransitProcessorAdmin
from .enrollment import EnrollmentEventAdmin, SortableEnrollmentFlowAdmin
from .users import (
    GOOGLE_USER_INFO_URL,
    add_staff_user_to_group,
    add_transit_agency_staff_user_to_group,
    add_google_sso_userinfo,
    is_staff_member,
    pre_login_user,
)

__all__ = [
    "PemDataAdmin",
    "ClaimsProviderAdmin",
    "TransitAgencyAdmin",
    "TransitProcessorAdmin",
    "EnrollmentEventAdmin",
    "SortableEnrollmentFlowAdmin",
    "GOOGLE_USER_INFO_URL",
    "add_staff_user_to_group",
    "add_transit_agency_staff_user_to_group",
    "add_google_sso_userinfo",
    "is_staff_member",
    "pre_login_user",
]
