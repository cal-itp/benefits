from benefits.cli.agency.list import List
from benefits.cli.commands import BenefitsCommand


class Command(BenefitsCommand):
    """Work with transit agencies."""

    help = __doc__
    name = "agency"
    subcommands = [List]

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        # make List the default_subcmd
        super().__init__(stdout, stderr, no_color, force_color, List)
