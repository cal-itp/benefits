from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

from authlib.integrations.django_client import OAuth

from benefits.core import middleware, session


_oauth = OAuth()


@decorator_from_middleware(middleware.AgencySessionRequired)
@decorator_from_middleware(middleware.VerifierSessionRequired)
def login(request):
    verifier = session.verifier(request)
    if not verifier.requires_authentication:
        return redirect(session.origin(request))

    oauth_client = _oauth.create_client(verifier.auth_provider.name)

    if not oauth_client:
        return redirect(session.origin(request))

    redirect_uri = reverse("oauth:authorize")
    return oauth_client.authorize_redirect(request, redirect_uri)


@decorator_from_middleware(middleware.AgencySessionRequired)
@decorator_from_middleware(middleware.VerifierSessionRequired)
def authorize(request):
    verifier = session.verifier(request)
    if not verifier.requires_authentication:
        return redirect(session.origin(request))

    oauth_client = _oauth.create_client(verifier.auth_provider.name)

    token = oauth_client.authorize_access_token(request)

    if token is None:
        return redirect(session.origin(request))
    else:
        session.update(request, auth=True)
        return redirect("eligibility:confirm")
