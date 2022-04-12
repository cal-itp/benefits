from django.shortcuts import redirect
from django.urls import reverse

from authlib.integrations.django_client import OAuth

from benefits.core import session
from benefits.settings import OAUTH_CLIENT_NAME


_oauth = OAuth()
_oauth.register(OAUTH_CLIENT_NAME)
oauth_client = _oauth.create_client(OAUTH_CLIENT_NAME)


def login(request):
    if not oauth_client:
        raise Exception("No OAuth client")

    route = reverse("oauth:authorize")
    redirect_uri = request.build_absolute_uri(route)

    return oauth_client.authorize_redirect(request, redirect_uri)


def authorize(request):
    if not oauth_client:
        raise Exception("No OAuth client")

    token = oauth_client.authorize_access_token(request)

    if token is None:
        return redirect(session.origin(request))
    else:
        session.update(request, auth=True)
        return redirect("eligibility:confirm")
