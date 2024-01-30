import requests

from django.conf import settings
from loguru import logger


def pre_login_user(user, request):
    logger.debug(f"Running pre-login callback for user: {user.username}")
    token = request.session.get("google_sso_access_token")
    if token:
        headers = {
            "Authorization": f"Bearer {token}",
        }

        # Request Google user info to get name and email
        url = "https://www.googleapis.com/oauth2/v3/userinfo"
        response = requests.get(url, headers=headers, timeout=settings.REQUESTS_TIMEOUT)
        user_data = response.json()
        logger.debug(f"Updating admin user data from Google for user with email: {user_data['email']}")

        user.first_name = user_data["given_name"]
        user.last_name = user_data["family_name"]
        user.username = user_data["email"]
        user.email = user_data["email"]
        user.save()
