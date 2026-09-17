from benefits.routes import Routes as BenefitsRoutes


class Routes(BenefitsRoutes):
    """Django routes in the form of `app:name` for this app."""

    @property
    def ENROLLMENT_LITTLEPAY_INDEX(self):
        """Start of the enrollment phase, using Littlepay."""
        return "littlepay:index"

    @property
    def ENROLLMENT_LITTLEPAY_TOKEN(self):
        """Acquire a Littlepay card tokenization access token for enrollment."""
        return "littlepay:token"


routes = Routes()
