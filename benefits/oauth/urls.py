from cdt_identity import views as cdt_identity_views
from cdt_identity.routes import Routes
from cdt_identity.urls import app_name as cdt_app_name
from django.utils.decorators import decorator_from_middleware
from django.urls import path

from benefits.routes import routes
from . import views, hooks
from .middleware import FlowUsesClaimsVerificationSessionRequired

# use cdt_identity app name so that the URL namespace matches what cdt_identity expects.
# (e.g. when cdt_identity reverses routes.)
app_name = cdt_app_name
urlpatterns = [
    # /oauth
    path(
        Routes.login,
        decorator_from_middleware(FlowUsesClaimsVerificationSessionRequired)(cdt_identity_views.login),
        {"hooks": hooks.OAuthHooks},
        name=routes.name(routes.OAUTH_LOGIN),
    ),
    path(
        Routes.authorize,
        decorator_from_middleware(FlowUsesClaimsVerificationSessionRequired)(cdt_identity_views.authorize),
        {"hooks": hooks.OAuthHooks},
        name=routes.name(routes.OAUTH_AUTHORIZE),
    ),
    path(
        Routes.cancel,
        decorator_from_middleware(FlowUsesClaimsVerificationSessionRequired)(cdt_identity_views.cancel),
        {"hooks": hooks.OAuthHooks},
        name=routes.name(routes.OAUTH_CANCEL),
    ),
    path(
        Routes.logout,
        decorator_from_middleware(FlowUsesClaimsVerificationSessionRequired)(cdt_identity_views.logout),
        {"hooks": hooks.OAuthHooks},
        name=routes.name(routes.OAUTH_LOGOUT),
    ),
    path(
        Routes.post_logout,
        decorator_from_middleware(FlowUsesClaimsVerificationSessionRequired)(cdt_identity_views.post_logout),
        {"hooks": hooks.OAuthHooks},
        name=routes.name(routes.OAUTH_POST_LOGOUT),
    ),
    path("error", views.system_error, name=routes.name(routes.OAUTH_SYSTEM_ERROR)),
]
