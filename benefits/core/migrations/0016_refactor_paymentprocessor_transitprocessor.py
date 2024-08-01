# Generated by Django 5.0.7 on 2024-07-31 22:41

from django.contrib.auth.management import create_permissions
from django.db import migrations, models

import benefits.core.models
import benefits.secrets


def create_all_permissions(apps, schema_editor):
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def update_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    staff_group = Group.objects.get(name="Cal-ITP")

    Permission = apps.get_model("auth", "Permission")

    remove_permissions = ["Can view", "Can change", "Can add", "Can delete"]
    for remove_permission in remove_permissions:
        current_permission = Permission.objects.get(name=f"{remove_permission} payment processor")
        staff_group.permissions.remove(current_permission)
        current_permission.delete()

    add_permissions = ["Can view", "Can change"]
    for add_permission in add_permissions:
        new_permission = Permission.objects.get(name=f"{add_permission} transit processor")
        staff_group.permissions.add(new_permission)


def migrate_data(apps, schema_editor):
    TransitAgency = apps.get_model("core", "TransitAgency")

    for agency in TransitAgency.objects.all():
        agency.transit_processor_audience = agency.transit_processor.audience
        agency.transit_processor_client_id = agency.transit_processor.client_id
        agency.transit_processor_client_secret_name = agency.transit_processor.client_secret_name
        agency.save()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_staff_group_edit_permissions"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="PaymentProcessor",
            new_name="TransitProcessor",
        ),
        migrations.RenameField(
            model_name="transitagency",
            old_name="payment_processor",
            new_name="transit_processor",
        ),
        migrations.RunPython(create_all_permissions),
        migrations.RunPython(update_permissions),
        migrations.AddField(
            model_name="transitagency",
            name="transit_processor_audience",
            field=models.TextField(
                default="", help_text="This agency's audience value used to access the TransitProcessor's API."
            ),
        ),
        migrations.AddField(
            model_name="transitagency",
            name="transit_processor_client_id",
            field=models.TextField(
                default="", help_text="This agency's client_id value used to access the TransitProcessor's API."
            ),
        ),
        migrations.AddField(
            model_name="transitagency",
            name="transit_processor_client_secret_name",
            field=benefits.core.models.SecretNameField(
                default="",
                help_text="The name of the secret containing this agency's client_secret value used to access the TransitProcessor's API.",  # noqa: E501
                max_length=127,
                validators=[benefits.secrets.SecretNameValidator()],
            ),
        ),
        migrations.RunPython(migrate_data),
        migrations.RemoveField(
            model_name="transitprocessor",
            name="audience",
        ),
        migrations.RemoveField(
            model_name="transitprocessor",
            name="client_id",
        ),
        migrations.RemoveField(
            model_name="transitprocessor",
            name="client_secret_name",
        ),
        migrations.AlterField(
            model_name="transitprocessor",
            name="api_base_url",
            field=models.TextField(help_text="The absolute base URL for the TransitProcessor's API, including https://."),
        ),
        migrations.AlterField(
            model_name="transitprocessor",
            name="card_tokenize_env",
            field=models.TextField(help_text="The environment in which card tokenization is occurring."),
        ),
        migrations.AlterField(
            model_name="transitprocessor",
            name="card_tokenize_func",
            field=models.TextField(
                help_text="The function from the card tokenization library to call on the client to initiate the process."
            ),
        ),
        migrations.AlterField(
            model_name="transitprocessor",
            name="card_tokenize_url",
            field=models.TextField(
                help_text="The abolute URL for the client-side card tokenization library provided by the TransitProcessor."
            ),
        ),
        migrations.AlterField(
            model_name="transitprocessor",
            name="name",
            field=models.TextField(
                help_text="Primary internal display name for this TransitProcessor instance, e.g. in the Admin."
            ),
        ),
    ]
