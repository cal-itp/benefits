# Generated by Django 5.1.7 on 2025-03-14 20:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0038_remove_enrollmentflow_eligibility_start_template_override"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="enrollmentflow",
            name="help_template",
        ),
    ]
