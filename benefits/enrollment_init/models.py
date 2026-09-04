import logging

from django.core.exceptions import ValidationError
from django.db import models

from benefits.core.models import EnrollmentGroup, TransitProcessorConfig

logger = logging.getLogger(__name__)


class InitConfig(TransitProcessorConfig):
    """Configuration for connecting to Switchio, an entity that applies transit agency fare rules to rider transactions."""

    tokenization_api_key = models.TextField(
        help_text="The API key used to access Collect.js for tokenization.", default="", blank=True
    )

    def clean(self):
        field_errors = {}

        if self.pk and self.transitagency_set and any([agency.active for agency in self.transitagency_set.all()]):
            message = "This field is required when this configuration is referenced by an active transit agency."
            needed = dict(
                tokenization_api_key=self.tokenization_api_key,
            )
            field_errors.update({k: ValidationError(message) for k, v in needed.items() if not v})

        if field_errors:
            raise ValidationError(field_errors)


class InitGroup(EnrollmentGroup):
    group_id = models.IntegerField(default=None, blank=True, help_text="The ID of the INIT group for user enrollment.")

    @staticmethod
    def by_id(id):
        """Get a LittlepayGroup instance by its ID."""
        logger.debug(f"Get {InitGroup.__name__} by id: {id}")
        return InitGroup.objects.get(id=id)
