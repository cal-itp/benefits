"""Create Cal-ITP staff group

Originally from 0013_create_staff_group.py, this group needs to be created immediately
so that unguarded queries for the group named in the default `STAFF_GROUP_NAME` setting
do not fail right out of the gate.
"""

from django.db import migrations


def create_staff_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="Cal-ITP")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_reset_20260226"),
    ]

    operations = [migrations.RunPython(create_staff_group)]
