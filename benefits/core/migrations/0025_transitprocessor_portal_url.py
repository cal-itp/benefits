# Generated by Django 5.0.6 on 2024-09-16 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0024_transitagency_sso_domain_customer_service"),
    ]

    operations = [
        migrations.AddField(
            model_name="transitprocessor",
            name="portal_url",
            field=models.TextField(
                blank=True,
                help_text="The absolute base URL for the TransitProcessor's control portal, including https://.",
                null=True,
            ),
        ),
    ]
