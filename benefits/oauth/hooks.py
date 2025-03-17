from cdt_identity.hooks import DefaultHooks

from . import analytics


class OAuthHooks(DefaultHooks):
    @classmethod
    def pre_login(cls, request):
        super().pre_login(request)
        analytics.started_sign_in(request)
