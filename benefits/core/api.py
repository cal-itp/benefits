

class Response():
    """Base API response."""

    def __init__(self, status_code, error=None, message=None):
        self.status_code = status_code
        self._assign_error(error=error, message=message)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.status_code)

    def _assign_error(self, error=None, message=None):
        if not any([error, message]):
            return
        self.error = (message if not error else f"{message}: {str(error)}") if message else str(error)

    def is_error(self):
        return self.error is not None

    def is_success(self):
        return self.status_code == 200
