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

    @property
    def ELIGIBILITY_INDEX(self):
        """Start of eligibility phase, the user picks a flow."""
        return "eligibility:index"

    @property
    def ELIGIBILITY_AGENCY_INDEX(self):
        """The user picks a flow and a transit agency is configured for them."""
        return "eligibility:agency_index"

    @property
    def ELIGIBILITY_START(self):
        """Flow-specific eligibility information."""
        return "eligibility:start"

    @property
    def ELIGIBILITY_CONFIRM(self):
        """Agency card specific eligibility form."""
        return "eligibility:confirm"

    @property
    def ELIGIBILITY_UNVERIFIED(self):
        """The user's eligibility was not verified."""
        return "eligibility:unverified"

    @staticmethod
    def name(route: str) -> str:
        """Returns just the name portion of the app:name structure of the route."""
        return route.split(":")[-1]


routes = Routes()
