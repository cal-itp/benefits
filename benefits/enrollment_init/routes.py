from benefits.routes import Routes as BenefitsRoutes


class Routes(BenefitsRoutes):
    """Django routes in the form of `app:name` for this app."""

    @property
    def ENROLLMENT_INIT_INDEX(self):
        """Start of the enrollment phase, using INIT."""
        return "init:index"


routes = Routes()
