from benefits.routes import Routes as BenefitsRoutes


class Routes(BenefitsRoutes):
    """Django routes in the form of `app:name` for this app."""

    @property
    def ENROLLMENT_SWITCHIO_INDEX(self):
        """Start of the enrollment phase, using Switchio."""
        return "switchio:index"

    @property
    def ENROLLMENT_SWITCHIO_GATEWAY_URL(self):
        """Establish a registration request and receive back a tokenization gateway URL."""
        return "switchio:gateway_url"


routes = Routes()
