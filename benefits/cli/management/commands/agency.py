from benefits.cli.commands import BenefitsCommand


class Command(BenefitsCommand):
    """Work with transit agencies."""

    help = __doc__
    name = "agency"
    subcommands = []

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
