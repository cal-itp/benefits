"""
The core application: Common model definitions.
"""
from django.db import models
from django.urls import reverse


class EligibilityType(models.Model):
    """A single conditional eligibility type."""

    name = models.TextField()
    label = models.TextField()
    group_id = models.TextField()

    def __str__(self):
        return self.label


class EligibilityVerifier(models.Model):
    """An entity that verifies eligibility."""

    name = models.TextField()
    api_url = models.TextField()
    eligibility_types = models.ManyToManyField(EligibilityType)

    def __str__(self):
        return self.name

    @property
    def eligibility_set(self):
        """Set of eligibility_type names"""
        return set(self.eligibility_types.values_list("name", flat=True))


class TransitAgency(models.Model):
    """An agency offering transit service."""

    slug = models.TextField()
    short_name = models.TextField()
    long_name = models.TextField()
    agency_id = models.TextField()
    mechant_id = models.TextField()
    logo_url = models.URLField()
    street_address1 = models.TextField()
    street_address2 = models.TextField(blank=True)
    city = models.TextField()
    zipcode = models.TextField()
    phone = models.TextField()
    active = models.BooleanField(default=False)
    eligibility_types = models.ManyToManyField(EligibilityType)
    eligibility_verifiers = models.ManyToManyField(EligibilityVerifier)

    def __str__(self):
        return self.long_name

    @property
    def eligibility_set(self):
        """Set of eligibility_type names"""
        return set(self.eligibility_types.values_list("name", flat=True))

    @property
    def index_url(self):
        """Url to the TransitAgency's landing page."""
        return reverse("core:agency_index", args=[self.slug])

    @staticmethod
    def by_id(id):
        """Get a TransitAgency instance by its ID."""
        return TransitAgency.objects.get(id=id)

    @staticmethod
    def by_slug(slug):
        """Get a TransitAgency instance by its slug."""
        return TransitAgency.objects.filter(slug=slug).first()

    @staticmethod
    def all_active():
        """Get all TransitAgency instances marked active."""
        return TransitAgency.objects.filter(active=True)
