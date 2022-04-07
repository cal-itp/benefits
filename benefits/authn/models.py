# https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.Field(primary_key=True)

    # don't persist to database
    # https://stackoverflow.com/a/22690832/358804
    def save(self, *args, **kwargs):
        pass

    class Meta:
        managed = False
