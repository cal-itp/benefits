# Generated by Django 5.0.7 on 2024-08-06 19:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0018_rename_eligibility_api_fields"),
    ]

    operations = [
        migrations.RenameField(model_name="transitagency", old_name="agency_id", new_name="eligibility_api_id"),
        migrations.RenameField(
            model_name="transitagency", old_name="jws_signing_alg", new_name="eligibility_api_jws_signing_alg"
        ),
        migrations.RenameField(model_name="transitagency", old_name="private_key", new_name="eligibility_api_private_key"),
        migrations.RenameField(model_name="transitagency", old_name="public_key", new_name="eligibility_api_public_key"),
        migrations.AlterField(
            model_name="transitagency",
            name="active",
            field=models.BooleanField(default=False, help_text="Determines if this Agency is enabled for users"),
        ),
        migrations.AlterField(
            model_name="transitagency",
            name="eligibility_api_id",
            field=models.TextField(help_text="The identifier for this agency used in Eligibility API calls."),
        ),
        migrations.AlterField(
            model_name="transitagency",
            name="eligibility_api_jws_signing_alg",
            field=models.TextField(help_text="The JWS-compatible signing algorithm used in Eligibility API calls."),
        ),
        migrations.AlterField(
            model_name="transitagency",
            name="eligibility_api_private_key",
            field=models.ForeignKey(
                help_text="Private key used to sign Eligibility API tokens created on behalf of this Agency.",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="core.pemdata",
            ),
        ),
        migrations.AlterField(
            model_name="transitagency",
            name="eligibility_api_public_key",
            field=models.ForeignKey(
                help_text="Public key corresponding to the agency's private key, used by Eligibility Verification servers to encrypt responses.",  # noqa: E501
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="core.pemdata",
            ),
        ),
        migrations.AlterField(
            model_name="transitagency",
            name="eligibility_index_template",
            field=models.TextField(help_text="The template used for this agency's eligibility landing page"),
        ),
        migrations.AlterField(
            model_name="transitagency",
            name="index_template",
            field=models.TextField(help_text="The template used for this agency's landing page"),
        ),
        migrations.AlterField(
            model_name="transitagency",
            name="info_url",
            field=models.URLField(help_text="URL of a website/page with more information about the agency's discounts"),
        ),
        migrations.AlterField(
            model_name="transitagency",
            name="long_name",
            field=models.TextField(
                help_text="The user-facing long name for this agency. Often the short_name acronym, spelled out."
            ),
        ),
        migrations.AlterField(
            model_name="transitagency",
            name="phone",
            field=models.TextField(help_text="Agency customer support phone number"),
        ),
        migrations.AlterField(
            model_name="transitagency",
            name="short_name",
            field=models.TextField(help_text="The user-facing short name for this agency. Often an uppercase acronym."),
        ),
        migrations.AlterField(
            model_name="transitagency",
            name="slug",
            field=models.TextField(
                help_text="Used for URL navigation for this agency, e.g. the agency homepage url is /{slug}"
            ),
        ),
    ]