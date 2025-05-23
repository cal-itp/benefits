# Generated by Django 5.1.7 on 2025-03-24 13:43

import django.db.models.deletion
from django.db import migrations, models


def migrate_data(apps, schema_editor):
    EnrollmentFlow = apps.get_model("core", "EnrollmentFlow")
    ClaimsVerificationRequest = apps.get_model("cdt_identity", "ClaimsVerificationRequest")

    idg_systems = ["calfresh", "medicare", "senior", "veteran"]

    for idg_system in idg_systems:
        flow = EnrollmentFlow.objects.filter(system_name=idg_system).first()
        if flow:
            claims_verification_request = ClaimsVerificationRequest.objects.create(
                system_name=flow.system_name,
                scopes=flow.claims_scope,
                eligibility_claim=flow.claims_eligibility_claim,
                extra_claims=flow.claims_extra_claims,
                scheme=flow.claims_scheme_override,
            )
            claims_verification_request.save()

    for flow in EnrollmentFlow.objects.all():
        if flow.system_name in idg_systems:
            flow.claims_request = ClaimsVerificationRequest.objects.get(system_name=flow.system_name)
            flow.save()


class Migration(migrations.Migration):

    dependencies = [
        ("cdt_identity", "0001_initial"),
        ("core", "0042_remove_enrollmentflow_enrollment_success_template_override"),
    ]

    operations = [
        migrations.AddField(
            model_name="enrollmentflow",
            name="claims_request",
            field=models.ForeignKey(
                blank=True,
                help_text="The claims request details for this flow.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="cdt_identity.claimsverificationrequest",
            ),
        ),
        migrations.RunPython(migrate_data),
        migrations.RemoveField(
            model_name="enrollmentflow",
            name="claims_scope",
        ),
        migrations.RemoveField(
            model_name="enrollmentflow",
            name="claims_eligibility_claim",
        ),
        migrations.RemoveField(
            model_name="enrollmentflow",
            name="claims_extra_claims",
        ),
        migrations.RemoveField(
            model_name="enrollmentflow",
            name="claims_scheme_override",
        ),
    ]
