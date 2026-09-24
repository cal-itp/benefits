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

    @property
    def IN_PERSON_ENROLLMENT_LITTLEPAY_INDEX(self):
        """In-person (e.g. agency assisted) enrollment using Littlepay"""
        return "in_person:enrollment_littlepay_index"

    @property
    def IN_PERSON_ENROLLMENT_LITTLEPAY_TOKEN(self):
        """Acquire a Littlepay access token for in-person enrollment."""
        return "in_person:enrollment_littlepay_token"


routes = Routes()
