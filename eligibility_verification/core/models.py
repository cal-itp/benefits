import uuid


from django.db import models


class EligibilityType(models.Model):
    short_name = models.CharField(max_length=10)
    long_name = models.CharField(max_length=25)
    group_id = models.UUIDField(default=uuid.uuid4())

    def __str__(self):
        return self.long_name


class TransitAgency(models.Model):
    short_name = models.CharField(max_length=5)
    long_name = models.CharField(max_length=25)
    agency_id = models.CharField(max_length=50)
    mechant_id = models.UUIDField(default=uuid.uuid4())
    logo_url = models.URLField()
    street_address1 = models.CharField(max_length=25)
    street_address2 = models.CharField(max_length=25, blank=True)
    city = models.CharField(max_length=25)
    zipcode = models.CharField(max_length=5)
    eligibility_types = models.ManyToManyField(EligibilityType)

    def __str__(self):
        return self.long_name
