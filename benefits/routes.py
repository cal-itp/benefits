class Routes:
    """Django routes in the form of `app:name` for the Benefits application."""

    @property
    def INDEX(self):
        """Entry point to the app."""
        return "core:index"

    @property
    def HELP(self):
        """Application help page."""
        return "core:help"

    @property
    def LOGGED_OUT(self):
        """The user has logged out of OAuth for claims verification."""
        return "core:logged_out"

    @property
    def SERVER_ERROR(self):
        """Generic 500 handler."""
        return "core:server-error"

    @property
    def AGENCY_INDEX(self):
        """The landing page for an agency."""
        return "core:agency_index"

    @property
    def AGENCY_PUBLIC_KEY(self):
        """Agency's eligibility API public key."""
        return "core:agency_public_key"

    @property
    def OAUTH_LOGIN(self):
        """Start of the identity proofing phase for claims verification."""
        return "oauth:login"

    @property
    def OAUTH_CANCEL(self):
        """OAuth cancel login."""
        return "oauth:cancel"

    @property
    def OAUTH_AUTHORIZE(self):
        """OAuth authorize access token for claims verification."""
        return "oauth:authorize"

    @property
    def OAUTH_LOGOUT(self):
        """OAuth initiate logout."""
        return "oauth:logout"

    @property
    def OAUTH_POST_LOGOUT(self):
        """OAuth complete logout."""
        return "oauth:post_logout"

    @property
    def OAUTH_SYSTEM_ERROR(self):
        """OAuth error not caused by the user."""
        return "oauth:system-error"

    @staticmethod
    def name(route: str) -> str:
        """Returns just the name portion of the app:name structure of the route."""
        return route.split(":")[-1]


routes = Routes()
