from benefits.core import session
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

# https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#django.contrib.auth.get_user_model
User = get_user_model()


class SessionBackend(BaseBackend):
    def authenticate(self, request):
        # TODO THIS IS NOT PROPER AUTHENTICATION. Just implemented this way for testing.
        session.update(request, auth=True)

        user = User()
        return user

    def get_user(self, user_id):
        user = User()
        return user
