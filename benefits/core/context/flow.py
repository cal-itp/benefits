from django.db import models


class SystemName(models.TextChoices):
    CALFRESH = "calfresh"
    COURTESY_CARD = "courtesy_card"
    MEDICARE = "medicare"
    OLDER_ADULT = "senior"
    REDUCED_FARE_MOBILITY_ID = "mobility_pass"
    VETERAN = "veteran"
