from dataclasses import dataclass

from django.db.models import Q

from benefits.cli.commands import BaseOptions, BenefitsCommand
from benefits.core.models import TransitAgency


@dataclass
class Options(BaseOptions):
    all: bool = False
    name: str = None
    slug: str = None


class List(BenefitsCommand):
    """List transit agencies."""

    help = __doc__
    name = "list"
    options_cls = Options

    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            default=False,
            help="Show both active and inactive agencies. By default show only active agencies.",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            help="Filter for agencies with matching (partial) short_name or long_name.",
        )
        parser.add_argument(
            "-s",
            "--slug",
            type=str,
            help="Filter for agencies with matching (partial) slug.",
        )

    def handle(self, *args, **options):
        opts = self.parse_opts(**options)
        agencies = TransitAgency.objects.all()

        if not opts.all:
            agencies = agencies.filter(active=True)

        if opts.name:
            q = Q(short_name__contains=opts.name) | Q(long_name__contains=opts.name)
            agencies = agencies.filter(q)

        if opts.slug:
            agencies = agencies.filter(slug__contains=opts.slug)

        if len(agencies) > 0:
            if len(agencies) > 1:
                msg = f"{len(agencies)} agencies:"
            else:
                msg = "1 agency:"
            self.stdout.write(self.style.SUCCESS(msg))

            active = filter(lambda a: a.active, agencies)
            inactive = filter(lambda a: not a.active, agencies)

            for agency in active:
                self.stdout.write(self.style.HTTP_NOT_MODIFIED(f"{agency}"))
            for agency in inactive:
                self.stdout.write(self.style.WARNING(f"[inactive] {agency}"))
        else:
            self.stdout.write(self.style.HTTP_NOT_FOUND("No matching agencies"))
