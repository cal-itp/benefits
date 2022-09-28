# Generated by Django 4.1 on 2022-09-02 18:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AuthProvider",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("sign_in_button_label", models.TextField()),
                ("sign_out_button_label", models.TextField()),
                ("client_name", models.TextField()),
                ("client_id", models.TextField()),
                ("authority", models.TextField()),
                ("scope", models.TextField(null=True)),
                ("claim", models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="EligibilityType",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.TextField()),
                ("label", models.TextField()),
                ("group_id", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="EligibilityVerifier",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.TextField()),
                ("api_url", models.TextField(null=True)),
                ("api_auth_header", models.TextField(null=True)),
                ("api_auth_key", models.TextField(null=True)),
                ("jwe_cek_enc", models.TextField(null=True)),
                ("jwe_encryption_alg", models.TextField(null=True)),
                ("jws_signing_alg", models.TextField(null=True)),
                ("selection_label", models.TextField()),
                ("selection_label_description", models.TextField(null=True)),
                ("start_content_title", models.TextField()),
                ("start_item_name", models.TextField()),
                ("start_item_description", models.TextField()),
                ("start_blurb", models.TextField()),
                ("form_title", models.TextField(null=True)),
                ("form_content_title", models.TextField(null=True)),
                ("form_blurb", models.TextField(null=True)),
                ("form_sub_label", models.TextField(null=True)),
                ("form_sub_help_text", models.TextField(null=True)),
                ("form_sub_placeholder", models.TextField(null=True)),
                ("form_sub_pattern", models.TextField(null=True)),
                ("form_name_label", models.TextField(null=True)),
                ("form_name_help_text", models.TextField(null=True)),
                ("form_name_placeholder", models.TextField(null=True)),
                ("form_name_max_length", models.PositiveSmallIntegerField(null=True)),
                ("unverified_title", models.TextField()),
                ("unverified_content_title", models.TextField()),
                ("unverified_blurb", models.TextField()),
                (
                    "auth_provider",
                    models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to="core.authprovider"),
                ),
                (
                    "eligibility_type",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="core.eligibilitytype"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PaymentProcessor",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.TextField()),
                ("api_base_url", models.TextField()),
                ("api_access_token_endpoint", models.TextField()),
                ("api_access_token_request_key", models.TextField()),
                ("api_access_token_request_val", models.TextField()),
                ("card_tokenize_url", models.TextField()),
                ("card_tokenize_func", models.TextField()),
                ("card_tokenize_env", models.TextField()),
                ("customer_endpoint", models.TextField()),
                ("customers_endpoint", models.TextField()),
                ("group_endpoint", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="PemData",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("label", models.TextField()),
                ("text", models.TextField(null=True)),
                ("remote_url", models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="TransitAgency",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("slug", models.TextField()),
                ("short_name", models.TextField()),
                ("long_name", models.TextField()),
                ("agency_id", models.TextField()),
                ("merchant_id", models.TextField()),
                ("info_url", models.URLField()),
                ("phone", models.TextField()),
                ("active", models.BooleanField(default=False)),
                ("jws_signing_alg", models.TextField()),
                ("eligibility_types", models.ManyToManyField(to="core.eligibilitytype")),
                ("eligibility_verifiers", models.ManyToManyField(to="core.eligibilityverifier")),
                (
                    "payment_processor",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="core.paymentprocessor"),
                ),
                (
                    "private_key",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="core.pemdata"),
                ),
                (
                    "public_key",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="core.pemdata"),
                ),
            ],
        ),
        migrations.AddField(
            model_name="paymentprocessor",
            name="client_cert",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="core.pemdata"),
        ),
        migrations.AddField(
            model_name="paymentprocessor",
            name="client_cert_private_key",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="core.pemdata"),
        ),
        migrations.AddField(
            model_name="paymentprocessor",
            name="client_cert_root_ca",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="core.pemdata"),
        ),
        migrations.AddField(
            model_name="eligibilityverifier",
            name="public_key",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="core.pemdata"
            ),
        ),
    ]
