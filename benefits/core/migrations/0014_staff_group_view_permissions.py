from django.contrib.auth.management import create_permissions
from django.db import migrations


def create_all_permissions(apps, schema_editor):
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def add_view_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    staff_group = Group.objects.get(name="Cal-ITP")

    Permission = apps.get_model("auth", "Permission")
    permission_names = [
        "Can view auth provider",
        "Can view eligibility type",
        "Can view eligibility verifier",
        "Can view payment processor",
        "Can view transit agency",
    ]

    for name in permission_names:
        view_permission = Permission.objects.get(name=name)
        staff_group.permissions.add(view_permission)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0013_create_staff_group"),
    ]

    operations = [
        # create permissions at this point instead of waiting for the `auth` app's post-migrate signal
        # https://github.com/django/django/blob/082fe2b5a83571dec4aa97580af0fe8cf2a5214e/django/contrib/auth/apps.py#L19-L20
        migrations.RunPython(create_all_permissions),
        migrations.RunPython(add_view_permissions),
    ]
