# Generated by Django 5.0.3 on 2024-05-13 19:57

import benefits.core.models
import benefits.secrets
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_eligibilitytype_reenrollment_error_template"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eligibilityverifier",
            name="api_auth_key_secret_name",
            field=benefits.core.models.SecretNameField(
                blank=True, max_length=127, null=True, validators=[benefits.secrets.SecretNameValidator()]
            ),
        ),
        migrations.AlterField(
            model_name="pemdata",
            name="text_secret_name",
            field=benefits.core.models.SecretNameField(
                blank=True, max_length=127, null=True, validators=[benefits.secrets.SecretNameValidator()]
            ),
        ),
    ]
