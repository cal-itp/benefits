from django.shortcuts import redirect
from django.utils.http import urlencode

import sentry_sdk

from benefits.routes import routes
from . import analytics


def deauthorize_redirect(request, oauth_client, redirect_uri):
    """Helper implements OIDC signout via the `end_session_endpoint`."""

    # Authlib has not yet implemented `end_session_endpoint` as the OIDC Session Management 1.0 spec is still in draft
    # See https://github.com/lepture/authlib/issues/331#issuecomment-827295954 for more
    #
    # The implementation here was adapted from the same ticket: https://github.com/lepture/authlib/issues/331#issue-838728145
    try:
        metadata = oauth_client.load_server_metadata()
    except Exception as ex:
        analytics.error(request, message=str(ex), operation="load_server_metadata")
        sentry_sdk.capture_exception(ex)
        return redirect(routes.OAUTH_SYSTEM_ERROR)

    end_session_endpoint = metadata.get("end_session_endpoint")

    params = dict(client_id=oauth_client.client_id, post_logout_redirect_uri=redirect_uri)
    encoded_params = urlencode(params)
    end_session_url = f"{end_session_endpoint}?{encoded_params}"

    return redirect(end_session_url)


def generate_redirect_uri(request, redirect_path):
    redirect_uri = str(request.build_absolute_uri(redirect_path)).lower()

    # this is a temporary hack to ensure redirect URIs are HTTPS when the app is deployed
    # see https://github.com/cal-itp/benefits/issues/442 for more context
    # this follow-up is needed while we address the hosting architecture
    if not redirect_uri.startswith("http://localhost"):
        redirect_uri = redirect_uri.replace("http://", "https://")

    return redirect_uri
