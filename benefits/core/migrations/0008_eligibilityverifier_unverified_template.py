# Generated by Django 5.0.3 on 2024-04-24 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_eligibilitytype_enrollment_index_template"),
    ]

    operations = [
        migrations.AddField(
            model_name="eligibilityverifier",
            name="unverified_template",
            field=models.TextField(default="eligibility/unverified.html"),
        ),
    ]
