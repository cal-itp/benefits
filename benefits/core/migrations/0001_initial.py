from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BenefitsProvider",
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
                ("client_cert_pem", models.TextField(help_text="A certificate in PEM format, used for client certificate authentication to this Provider's API.")),  # noqa: E501
                ("client_cert_private_key_pem", models.TextField(help_text="The private key in PEM format used to sign the certificate.")),  # noqa: E501
                ("client_cert_root_ca_pem", models.TextField(help_text="The root CA bundle in PEM format used to verify the Provider's server.")),  # noqa: E501
                ("customer_endpoint", models.TextField()),
                # fmt: on
                ("customers_endpoint", models.TextField()),
                ("group_endpoint", models.TextField()),
            ],
        ),
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
            name="EligibilityVerifier",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.TextField()),
                ("api_url", models.TextField()),
                ("api_auth_header", models.TextField()),
                ("api_auth_key", models.TextField()),
                # fmt: off
                ("public_key_pem", models.TextField(help_text="The Verifier's public key in PEM format, used to encrypt requests targeted at this Verifier and to verify signed responses from this verifier.")),  # noqa: E501
                ("jwe_cek_enc", models.TextField(help_text="The JWE-compatible Content Encryption Key (CEK) key-length and mode")),  # noqa: E501
                ("jwe_encryption_alg", models.TextField(help_text="The JWE-compatible encryption algorithm")),
                # fmt: on
                ("jws_signing_alg", models.TextField(help_text="The JWS-compatible signing algorithm")),
                ("eligibility_types", models.ManyToManyField(to="core.EligibilityType")),
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
                ("logo_url", models.URLField()),
                ("phone", models.TextField()),
                ("active", models.BooleanField(default=False)),
                # fmt: off
                ("private_key_pem", models.TextField(help_text="The Agency's private key in PEM format, used to sign tokens created on behalf of this Agency.")),  # noqa: E501
                ("jws_signing_alg", models.TextField(help_text="The JWS-compatible signing algorithm.")),
                ("benefits_provider", models.ForeignKey(on_delete=models.deletion.PROTECT, to="core.benefitsprovider")),
                ("eligibility_types", models.ManyToManyField(to="core.EligibilityType")),
                ("eligibility_verifier", models.ForeignKey(on_delete=models.deletion.PROTECT, to="core.eligibilityverifier")),
                # fmt: on
            ],
        ),
    ]
