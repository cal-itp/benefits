# Generated by Django 5.0.6 on 2024-07-16 23:08

from django.db import migrations


def add_edit_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    staff_group = Group.objects.get(name="Cal-ITP")

    Permission = apps.get_model("auth", "Permission")
    permission_names = [
        "Can change auth provider",
        "Can change eligibility type",
        "Can change eligibility verifier",
        "Can change payment processor",
        "Can change transit agency",
    ]

    for name in permission_names:
        edit_permission = Permission.objects.get(name=name)
        staff_group.permissions.add(edit_permission)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0014_staff_group_view_permissions"),
    ]

    operations = [migrations.RunPython(add_edit_permissions)]
