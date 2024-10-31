from dataclasses import dataclass
from pathlib import Path

from django.core.management.base import CommandError

from benefits.cli.commands import BaseOptions, BenefitsCommand
from benefits.core.models import TransitAgency, TransitProcessor


@dataclass
class Options(BaseOptions):
    active: bool = False
    info_url: str = None
    long_name: str = None
    phone: str = None
    short_name: str = None
    slug: str = None
    templates: bool = False
    templates_only: bool = False
    transit_processor: int = None

    def __post_init__(self):
        if not self.short_name:
            self.short_name = self.slug.upper()
        if not self.long_name:
            self.long_name = self.slug.upper()


class Create(BenefitsCommand):
    """Create a new transit agency."""

    help = __doc__
    name = "create"
    options_cls = Options
    sample_slug = "cst"
    templates = [
        f"core/index--{sample_slug}.html",
        f"eligibility/index--{sample_slug}.html",
    ]

    @property
    def template_paths(self):
        return [self.template_path(t) for t in self.templates]

    def _create_agency(self, opts: Options) -> TransitAgency:
        if isinstance(opts.transit_processor, int):
            transit_processor = TransitProcessor.objects.get(id=opts.transit_processor)
        else:
            transit_processor = None

        agency = TransitAgency.objects.create(
            active=opts.active,
            slug=opts.slug,
            info_url=opts.info_url,
            long_name=opts.long_name,
            phone=opts.phone,
            short_name=opts.short_name,
            transit_processor=transit_processor,
        )
        agency.save()

        return agency

    def _create_templates(self, agency: TransitAgency):
        for template in self.template_paths:
            content = template.read_text().replace(self.sample_slug, agency.slug)
            content = content.replace(self.sample_slug.upper(), agency.slug.upper())

            path = str(template.resolve()).replace(self.sample_slug, agency.slug)

            new_template = Path(path)
            new_template.write_text(content)

    def _raise_for_slug(self, opts: Options) -> bool:
        if TransitAgency.by_slug(opts.slug):
            raise CommandError(f"TransitAgency with slug already exists: {opts.slug}")

    def add_arguments(self, parser):
        parser.add_argument("-a", "--active", action="store_true", default=False, help="Activate the agency")
        parser.add_argument(
            "-i", "--info-url", type=str, default="https://agency.com", help="The agency's informational website URL"
        )
        parser.add_argument("-l", "--long-name", type=str, default="Regional Transit Agency", help="The agency's long name")
        parser.add_argument("-p", "--phone", type=str, default="800-555-5555", help="The agency's phone number")
        parser.add_argument("-s", "--short-name", type=str, default="Agency", help="The agency's short name")
        parser.add_argument("--templates", action="store_true", default=False, help="Also create templates for the agency")
        parser.add_argument(
            "--templates-only",
            action="store_true",
            default=False,
            help="Don't create the agency in the database, but scaffold templates",
        )
        parser.add_argument(
            "--transit-processor",
            type=int,
            choices=[t.id for t in TransitProcessor.objects.all()],
            default=TransitProcessor.objects.first().id,
            help="The id of a TransitProcessor instance to link to this agency",
        )
        parser.add_argument("slug", help="The agency's slug", type=str)

    def handle(self, *args, **options):
        opts = self.parse_opts(**options)
        self._raise_for_slug(opts)

        if not opts.templates_only:
            self.stdout.write(self.style.NOTICE("Creating new agency..."))
            agency = self._create_agency(opts)
            self.stdout.write(self.style.SUCCESS(f"Agency created: {agency.slug} (id={agency.id})"))

        if opts.templates:
            self.stdout.write(self.style.NOTICE("Creating new agency templates..."))
            self._create_templates(agency)
            self.stdout.write(self.style.SUCCESS("Templates created"))
