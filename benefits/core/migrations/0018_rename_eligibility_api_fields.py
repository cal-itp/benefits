# Generated by Django 5.0.7 on 2024-08-01 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_refactor_authprovider_claimsprovider"),
    ]

    operations = [
        migrations.RenameField(
            model_name="eligibilityverifier",
            old_name="api_auth_header",
            new_name="eligibility_api_auth_header",
        ),
        migrations.RenameField(
            model_name="eligibilityverifier",
            old_name="api_auth_key_secret_name",
            new_name="eligibility_api_auth_key_secret_name",
        ),
        migrations.RenameField(
            model_name="eligibilityverifier",
            old_name="jwe_cek_enc",
            new_name="eligibility_api_jwe_cek_enc",
        ),
        migrations.RenameField(
            model_name="eligibilityverifier",
            old_name="jwe_encryption_alg",
            new_name="eligibility_api_jwe_encryption_alg",
        ),
        migrations.RenameField(
            model_name="eligibilityverifier",
            old_name="jws_signing_alg",
            new_name="eligibility_api_jws_signing_alg",
        ),
        migrations.RenameField(
            model_name="eligibilityverifier",
            old_name="public_key",
            new_name="eligibility_api_public_key",
        ),
        migrations.RenameField(
            model_name="eligibilityverifier",
            old_name="api_url",
            new_name="eligibility_api_url",
        ),
        migrations.RenameField(
            model_name="eligibilityverifier",
            old_name="form_class",
            new_name="eligibility_form_class",
        ),
        migrations.RenameField(
            model_name="eligibilityverifier",
            old_name="start_template",
            new_name="eligibility_start_template",
        ),
        migrations.AlterField(
            model_name="eligibilityverifier",
            name="eligibility_start_template",
            field=models.TextField(default="eligibility/start.html"),
        ),
        migrations.RenameField(
            model_name="eligibilityverifier",
            old_name="unverified_template",
            new_name="eligibility_unverified_template",
        ),
    ]
