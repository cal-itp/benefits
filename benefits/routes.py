class Routes:
    """Django routes in the form of `app:name` for the Benefits application."""

    @staticmethod
    def name(route: str) -> str:
        """Returns just the name portion of the app:name structure of the route."""
        return route.split(":")[-1]


routes = Routes()
