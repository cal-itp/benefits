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


class TransitAgency(models.Model):
    """An agency offering transit service."""

    short_name = models.CharField(max_length=5)
    long_name = models.CharField(max_length=25)
    agency_id = models.CharField(max_length=50)
    mechant_id = models.CharField(max_length=50)
    logo_url = models.URLField()
    street_address1 = models.CharField(max_length=25)
    street_address2 = models.CharField(max_length=25, blank=True)
    city = models.CharField(max_length=25)
    zipcode = models.CharField(max_length=5)
    eligibility_verifiers = models.ManyToManyField(EligibilityVerifier)

    def __str__(self):
        return self.long_name

    @staticmethod
    def get(agency):
        return TransitAgency.objects.filter(short_name=agency)
