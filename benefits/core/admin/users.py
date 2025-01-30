import logging

from django.conf import settings
from django.contrib.auth.models import Group

import requests

from benefits.core import models


logger = logging.getLogger(__name__)


GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def add_google_sso_userinfo(user, request):
    token = request.session.get("google_sso_access_token")
    if token:
        headers = {
            "Authorization": f"Bearer {token}",
        }

        # Request Google user info to get name and email
        response = requests.get(GOOGLE_USER_INFO_URL, headers=headers, timeout=settings.REQUESTS_TIMEOUT)
        user_data = response.json()
        logger.debug(f"Updating user data from Google for user with email: {user_data['email']}")

        user.first_name = user_data["given_name"]
        user.last_name = user_data["family_name"]
        user.username = user_data["email"]
        user.email = user_data["email"]
        user.save()
    else:
        logger.warning("google_sso_access_token not found in session.")


def add_staff_user_to_group(user, request):
    if user.email in settings.GOOGLE_SSO_STAFF_LIST:
        staff_group = Group.objects.get(name=settings.STAFF_GROUP_NAME)
        staff_group.user_set.add(user)


def add_transit_agency_staff_user_to_group(user, request):
    user_sso_domain = user.email.split("@")[1]
    if user_sso_domain:
        agency = models.TransitAgency.objects.filter(sso_domain=user_sso_domain).first()
        if agency is not None and agency.staff_group:
            agency.staff_group.user_set.add(user)


def is_staff_member(user):
    """Determine if a user is a member of the staff group of Benefits

    The staff group of Benefits is also called the 'Cal-ITP' group (defined in settings.STAFF_GROUP_NAME)
    and it is not to be confused with Django's concept of 'staff' which simply means users that can log in to the admin.
    """

    staff_group = Group.objects.get(name=settings.STAFF_GROUP_NAME)
    return staff_group.user_set.contains(user)


def is_staff_member_or_superuser(user):
    """Determine if a user is a member of the staff group of Benefits or if it is a superuser."""
    return user.is_superuser or is_staff_member(user)


def pre_login_user(user, request):
    logger.debug(f"Running pre-login callback for user: {user.username}")
    add_google_sso_userinfo(user, request)
    add_staff_user_to_group(user, request)
    add_transit_agency_staff_user_to_group(user, request)
