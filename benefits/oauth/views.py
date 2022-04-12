from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

from authlib.integrations.django_client import OAuth

from benefits.core import middleware, session


_oauth = OAuth()
_oauth.register("oidc")


@decorator_from_middleware(middleware.AgencySessionRequired)
@decorator_from_middleware(middleware.VerifierSessionRequired)
def login(request):
    verifier = session.verifier(request)
    if not verifier.requires_authentication:
        return redirect(session.origin(request))

    oauth_client = _oauth.create_client(verifier.auth_provider.name)

    if not oauth_client:
        return redirect(session.origin(request))

    route = reverse("oauth:authorize")
    redirect_uri = request.build_absolute_uri(route)
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
