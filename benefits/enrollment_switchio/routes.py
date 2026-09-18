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

    @property
    def IN_PERSON_ENROLLMENT_SWITCHIO_INDEX(self):
        """In-person (e.g. agency assisted) enrollment using Switchio"""
        return "in_person:enrollment_switchio_index"

    @property
    def IN_PERSON_ENROLLMENT_SWITCHIO_GATEWAY_URL(self):
        """Switchio Gateway for in-person (e.g. agency assisted) enrollment"""
        return "in_person:enrollment_switchio_gateway"


routes = Routes()
