# Generated by Django 5.1.7 on 2025-07-03 22:10

import benefits.core.models.common
import benefits.secrets
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("enrollment_switchio", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="switchioconfig",
            name="api_key",
        ),
        migrations.RemoveField(
            model_name="switchioconfig",
            name="api_secret_name",
        ),
        migrations.AddField(
            model_name="switchioconfig",
            name="tokenization_api_key",
            field=models.TextField(
                blank=True, default="", help_text="The API key used to access the Switchio API for tokenization."
            ),
        ),
        migrations.AddField(
            model_name="switchioconfig",
            name="tokenization_api_secret_name",
            field=benefits.core.models.common.SecretNameField(
                blank=True,
                default="",
                help_text="The name of the secret containing the api_secret value used to access the Switchio API for tokenization.",  # noqa
                max_length=127,
                validators=[benefits.secrets.SecretNameValidator()],
            ),
        ),
        migrations.AddField(
            model_name="switchioconfig",
            name="enrollment_api_authorization_header",
            field=models.TextField(
                blank=True,
                default="",
                help_text="The value to use for the 'Authorization' header when accessing the Switchio API for enrollment.",
            ),
        ),
        migrations.AddField(
            model_name="switchioconfig",
            name="pto_id",
            field=models.PositiveIntegerField(
                blank=True,
                default=0,
                help_text="The Public Transport Operator ID to use with the Switchio API for enrollment.",
            ),
        ),
    ]
