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
        return "core:server_error"

    @property
    def AGENCY_INDEX(self):
        """The landing page for an agency."""
        return "core:agency_index"

    @property
    def AGENCY_CARD(self):
        """Agency card flow redirect for an agency."""
        return "core:agency_card"

    @property
    def AGENCY_ELIGIBILITY_INDEX(self):
        """The user picks a flow and a transit agency is configured for them."""
        return "core:agency_eligibility_index"

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
        return "oauth:system_error"

    @property
    def ELIGIBILITY_INDEX(self):
        """Start of eligibility phase, the user picks a flow."""
        return "eligibility:index"

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

    @property
    def ENROLLMENT_INDEX(self):
        """Start of the enrollment phase."""
        return "enrollment:index"

    @property
    def ENROLLMENT_TOKEN(self):
        """Acquire a TransitProcessor API token for enrollment."""
        return "enrollment:token"

    @property
    def ENROLLMENT_SUCCESS(self):
        """User has successfully enrolled and completed a Benefits flow."""
        return "enrollment:success"

    @property
    def ENROLLMENT_RETRY(self):
        """User entered their card details incorrectly or another recoverable problem."""
        return "enrollment:retry"

    @property
    def ENROLLMENT_REENROLLMENT_ERROR(self):
        """User tried to enroll when they are already enrolled in an expiring discount."""
        return "enrollment:reenrollment_error"

    @property
    def ENROLLMENT_SYSTEM_ERROR(self):
        """Enrollment error not caused by the user."""
        return "enrollment:system_error"

    @property
    def IN_PERSON_ELIGIBILITY(self):
        """In-person (e.g. agency assisted) eligibility"""
        return "in_person:eligibility"

    @property
    def IN_PERSON_ENROLLMENT(self):
        """In-person (e.g. agency assisted) enrollment"""
        return "in_person:enrollment"

    @property
    def IN_PERSON_ENROLLMENT_RETRY(self):
        """In-person user entered their card details incorrectly or another recoverable problem."""
        return "in_person:retry"

    @property
    def IN_PERSON_ENROLLMENT_REENROLLMENT_ERROR(self):
        """In-person user tried to enroll when they are already enrolled in an expiring discount."""
        return "in_person:reenrollment_error"

    @property
    def IN_PERSON_ENROLLMENT_SYSTEM_ERROR(self):
        """Enrollment error not caused by the user during in-person enrollment."""
        return "in_person:system_error"

    def to_dict(self) -> dict[str, str]:
        """Get a mapping of property name --> value for each `@property` in the Routes collection."""
        return {prop: str(getattr(self, prop)) for prop in dir(Routes) if isinstance(getattr(Routes, prop), property)}

    @staticmethod
    def name(route: str) -> str:
        """Returns just the name portion of the app:name structure of the route."""
        return route.split(":")[-1]


routes = Routes()
