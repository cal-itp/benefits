"""
The core application: Common model definitions.
"""
from django.db import models


class EligibilityType(models.Model):
    """A single conditional eligibility type."""

    name = models.CharField(max_length=25)
    label = models.CharField(max_length=50)
    group_id = models.CharField(max_length=50)

    def __str__(self):
        return self.label


class EligibilityVerifier(models.Model):
    """An entity that verifies eligibility."""

    name = models.CharField(max_length=25)
    api_url = models.CharField(max_length=50)
    eligibility_types = models.ManyToManyField(EligibilityType)

    def __str__(self):
        return self.name

    def eligibility_set(self):
        """Set of eligibility_type names"""
        return set(self.eligibility_types.values_list("name", flat=True))


class TransitAgency(models.Model):
    """An agency offering transit service."""

    slug = models.CharField(max_length=5)
    long_name = models.CharField(max_length=25)
    agency_id = models.CharField(max_length=50)
    mechant_id = models.CharField(max_length=50)
    logo_url = models.URLField()
    street_address1 = models.CharField(max_length=25)
    street_address2 = models.CharField(max_length=25, blank=True)
    city = models.CharField(max_length=25)
    zipcode = models.CharField(max_length=5)
    active = models.BooleanField(default=False)
    eligibility_types = models.ManyToManyField(EligibilityType)
    eligibility_verifiers = models.ManyToManyField(EligibilityVerifier)

    def __str__(self):
        return self.long_name

    def eligibility_set(self):
        """Set of eligibility_type names"""
        return set(self.eligibility_types.values_list("name", flat=True))

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
