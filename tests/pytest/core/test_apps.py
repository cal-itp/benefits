import pytest
from django.conf import settings
from django.contrib.auth.models import Group


@pytest.mark.django_db
def test_admin_group_is_created():
    assert Group.objects.filter(name=settings.STAFF_GROUP_NAME).exists()
