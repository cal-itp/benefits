from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0035_enrollmentflow_system_name_choices"),
    ]

    def migrate_in_person_flows(apps, schema_editor):
        EnrollmentFlow = apps.get_model("core", "EnrollmentFlow")
        for flow in EnrollmentFlow.objects.all():
            in_person = "in_person"  # value of EnrollmentMethods.IN_PERSON as of this migration
            if in_person in flow.supported_enrollment_methods:
                if flow.system_name not in [
                    "senior",
                    "medicare",
                    "courtesy_card",
                ]:  # the keys in `in_person.context.eligibility_index` as of this migration
                    flow.supported_enrollment_methods.remove(in_person)
                    flow.save()

    operations = [migrations.RunPython(migrate_in_person_flows)]
