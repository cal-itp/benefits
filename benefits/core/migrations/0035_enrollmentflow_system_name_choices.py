# Generated by Django 5.1.5 on 2025-02-20 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0034_transit_agency_index_context"),
    ]

    operations = [
        migrations.AlterField(
            model_name="enrollmentflow",
            name="system_name",
            field=models.SlugField(
                choices=[
                    ("agency_card", "Agency Card"),
                    ("calfresh", "Calfresh"),
                    ("courtesy_card", "Courtesy Card"),
                    ("medicare", "Medicare"),
                    ("senior", "Older Adult"),
                    ("mobility_pass", "Reduced Fare Mobility Id"),
                    ("veteran", "Veteran"),
                ],
                help_text="Primary internal system name for this EnrollmentFlow instance, e.g. in analytics and Eligibility API requests.",  # noqa
            ),
        ),
    ]
