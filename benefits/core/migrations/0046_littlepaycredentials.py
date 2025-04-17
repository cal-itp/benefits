# Generated by Django 5.1.7 on 2025-04-17 00:40

import benefits.core.models.common
import benefits.secrets
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0045_alter_transitagency_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="LittlepayCredentials",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "audience",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="The audience value used to access the Littlepay API.",
                    ),
                ),
                (
                    "client_id",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="The client_id value used to access the Littlepay API.",
                    ),
                ),
                (
                    "client_secret_name",
                    benefits.core.models.common.SecretNameField(
                        blank=True,
                        default="",
                        help_text="The name of the secret containing the client_secret value used to access the Littlepay API.",  # noqa
                        max_length=127,
                        validators=[benefits.secrets.SecretNameValidator()],
                    ),
                ),
            ],
        ),
    ]
