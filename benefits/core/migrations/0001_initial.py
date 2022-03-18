from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="EligibilityType",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.TextField()),
                ("label", models.TextField()),
                ("group_id", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="PemData",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("text", models.TextField(help_text="The data in utf-8 encoded PEM text format.")),
                ("label", models.TextField(help_text="Human description of the PEM data.")),
            ],
        ),
        migrations.CreateModel(
            name="EligibilityVerifier",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.TextField()),
                ("api_url", models.TextField()),
                ("api_auth_header", models.TextField()),
                ("api_auth_key", models.TextField()),
                # fmt: off
                ("form_sub_pattern", models.TextField(help_text="A regular expression used to validate the 'sub' API field before sending to this verifier", null=True)),  # noqa: E501
                ("form_name_max_length", models.PositiveSmallIntegerField(help_text="The maximum length accepted for the 'name' API field before sending to this verifier", null=True)),  # noqa: E501
                ("public_key", models.ForeignKey(help_text="The Verifier's public key, used to encrypt requests targeted at this Verifier and to verify signed responses from this verifier.", on_delete=models.deletion.PROTECT, related_name="+", to="core.PemData")),  # noqa: E501
                ("jwe_cek_enc", models.TextField(help_text="The JWE-compatible Content Encryption Key (CEK) key-length and mode")),  # noqa: E501
                ("jwe_encryption_alg", models.TextField(help_text="The JWE-compatible encryption algorithm")),
                # fmt: on
                ("jws_signing_alg", models.TextField(help_text="The JWS-compatible signing algorithm")),
                ("eligibility_types", models.ManyToManyField(to="core.EligibilityType")),
                ("selection_label", models.TextField()),
                ("selection_label_description", models.TextField(null=True)),
                ("instructions_title", models.TextField()),
                ("instructions_item_name", models.TextField()),
                ("instructions_item_description", models.TextField()),
                ("instructions_blurb", models.TextField()),
                ("form_title", models.TextField()),
                ("form_blurb", models.TextField()),
                ("form_sub_label", models.TextField()),
                ("form_sub_placeholder", models.TextField()),
                ("form_name_label", models.TextField()),
                ("form_name_placeholder", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="PaymentProcessor",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.TextField()),
                ("api_base_url", models.TextField()),
                ("api_access_token_endpoint", models.TextField()),
                ("api_access_token_request_key", models.TextField()),
                ("api_access_token_request_val", models.TextField()),
                ("card_tokenize_url", models.TextField()),
                ("card_tokenize_func", models.TextField()),
                ("card_tokenize_env", models.TextField()),
                # fmt: off
                ("client_cert", models.ForeignKey(help_text="The certificate used for client certificate authentication to the API.", on_delete=models.deletion.PROTECT, related_name="+", to="core.PemData")),  # noqa: E501
                ("client_cert_private_key", models.ForeignKey(help_text="The private key used to sign the certificate.", on_delete=models.deletion.PROTECT, related_name="+", to="core.PemData")),  # noqa: E501
                ("client_cert_root_ca", models.ForeignKey(help_text="The root CA bundle used to verify the server.", on_delete=models.deletion.PROTECT, related_name="+", to="core.PemData")),  # noqa: E501
                ("customer_endpoint", models.TextField()),
                # fmt: on
                ("customers_endpoint", models.TextField()),
                ("group_endpoint", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="TransitAgency",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.TextField()),
                ("short_name", models.TextField()),
                ("long_name", models.TextField()),
                ("agency_id", models.TextField()),
                ("merchant_id", models.TextField()),
                ("info_url", models.URLField()),
                ("phone", models.TextField()),
                ("active", models.BooleanField(default=False)),
                # fmt: off
                ("private_key", models.ForeignKey(help_text="The Agency's private key, used to sign tokens created on behalf of this Agency.", on_delete=models.deletion.PROTECT, related_name="+", to="core.PemData")),  # noqa: E501
                ("jws_signing_alg", models.TextField(help_text="The JWS-compatible signing algorithm.")),
                ("payment_processor", models.ForeignKey(on_delete=models.deletion.PROTECT, to="core.paymentprocessor")),
                ("eligibility_types", models.ManyToManyField(to="core.EligibilityType")),
                ("eligibility_verifiers", models.ManyToManyField(to="core.eligibilityverifier")),
                # fmt: on
            ],
        ),
    ]
