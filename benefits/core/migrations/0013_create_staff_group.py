from django.db import migrations


def create_staff_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="Cal-ITP")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_remove_transitagency_merchant_id"),
    ]

    operations = [migrations.RunPython(create_staff_group)]
