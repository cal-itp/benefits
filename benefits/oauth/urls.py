from cdt_identity import views as cdt_identity_views
from cdt_identity.routes import Routes
from cdt_identity.urls import app_name as cdt_app_name

from django.utils.decorators import decorator_from_middleware
from django.urls import path

from benefits.routes import routes
from . import views, hooks
from .middleware import FlowUsesClaimsVerificationSessionRequired


decorator = decorator_from_middleware(FlowUsesClaimsVerificationSessionRequired)
kwargs = {"hooks": hooks.OAuthHooks}

# use cdt_identity app name so that the URL namespace matches what cdt_identity expects.
# (e.g. when cdt_identity reverses routes.)
app_name = cdt_app_name
urlpatterns = [
    # /oauth
    path(Routes.login, decorator(cdt_identity_views.login), kwargs, name=Routes.login),
    path(Routes.authorize, decorator(cdt_identity_views.authorize), kwargs, name=Routes.authorize),
    path(Routes.cancel, decorator(cdt_identity_views.cancel), kwargs, name=Routes.cancel),
    path(Routes.logout, decorator(cdt_identity_views.logout), kwargs, name=Routes.logout),
    path(Routes.post_logout, decorator(cdt_identity_views.post_logout), kwargs, name=Routes.post_logout),
    path("error", views.SystemErrorView.as_view(), name=routes.name(routes.OAUTH_SYSTEM_ERROR)),
]
