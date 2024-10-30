from dataclasses import dataclass
from django.core.management.base import BaseCommand

from benefits import VERSION


@dataclass
class BaseOptions:
    skip_checks: bool = False
    verbosity: int = 1


class BenefitsCommand(BaseCommand):
    """Base class for Benefits CLI commands."""

    name = "benefits"
    help = __doc__
    options_cls = BaseOptions
    version = VERSION

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

    def get_version(self) -> str:
        """Override `BaseCommand.get_version()` to return the `benefits` version."""
        return self.version

    def parse_opts(self, **options):
        """Parse options into a dataclass instance."""
        options = {k: v for k, v in options.items() if k in dir(self.options_cls)}
        return self.options_cls(**options)
