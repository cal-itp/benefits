# Generated by Django 5.1 on 2024-09-13 04:55

import uuid
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0025_transitprocessor_portal_url"),
    ]

    operations = [
        migrations.CreateModel(
            name="EnrollmentEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ("enrollment_method", models.TextField(choices=[("digital", "digital"), ("in_person", "in_person")])),
                ("verified_by", models.TextField()),
                ("enrollment_datetime", models.DateTimeField(default=django.utils.timezone.now)),
                ("expiration_datetime", models.DateTimeField(blank=True, null=True)),
                ("enrollment_flow", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="core.enrollmentflow")),
                ("transit_agency", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="core.transitagency")),
            ],
        )
    ]
