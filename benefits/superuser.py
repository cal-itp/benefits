import os
import logging

from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()  # get the currently active user model

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
user = User.objects.filter(username=username)

if user.exists():
    if user.first().is_superuser:
        logger.debug("Skipping superuser creation since it already exists")
    else:
        raise RuntimeError("A user already exists with DJANGO_SUPERUSER_NAME as the username")
else:
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

    logger.debug("Creating superuser")
    User.objects.create_superuser(username, email, password)
