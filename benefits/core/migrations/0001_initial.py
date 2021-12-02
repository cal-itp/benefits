from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
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
                ("api_url", models.TextField()),
                ("api_auth_header", models.TextField()),
                ("api_auth_key", models.TextField()),
                (
                    "jwe_cek_enc",
                    models.TextField(help_text="The JWE-compatible Content Encryption Key (CEK) key-length and mode"),
                ),
                ("jwe_encryption_alg", models.TextField(help_text="The JWE-compatible encryption algorithm")),
                ("jws_signing_alg", models.TextField(help_text="The JWS-compatible signing algorithm")),
                ("eligibility_types", models.ManyToManyField(to="core.EligibilityType")),
            ],
        ),
        migrations.CreateModel(
            name="I18nText",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("label", models.TextField()),
                ("text", models.TextField()),
                ("text_en", models.TextField(null=True)),
                ("text_es", models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Icon",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("file", models.FileField(upload_to="img/icon/")),
                ("alt", models.ForeignKey(on_delete=models.deletion.PROTECT, related_name="+", to="core.i18ntext")),
            ],
        ),
        migrations.CreateModel(
            name="Image",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("file", models.FileField(upload_to="img/")),
                ("alt", models.ForeignKey(on_delete=models.deletion.PROTECT, related_name="+", to="core.i18ntext")),
            ],
        ),
        migrations.CreateModel(
            name="MediaItem",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "details",
                    models.ForeignKey(on_delete=models.deletion.PROTECT, related_name="+", to="core.i18ntext"),
                ),
                (
                    "heading",
                    models.ForeignKey(on_delete=models.deletion.PROTECT, related_name="+", to="core.i18ntext"),
                ),
                ("icon", models.ForeignKey(on_delete=models.deletion.PROTECT, related_name="+", to="core.icon")),
            ],
        ),
        migrations.CreateModel(
            name="Page",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("label", models.TextField()),
                ("classes", models.JSONField(blank=True, null=True)),
                (
                    "content_title",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.PROTECT,
                        related_name="+",
                        to="core.i18ntext",
                    ),
                ),
                (
                    "icon",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=models.deletion.PROTECT, related_name="+", to="core.icon"
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=models.deletion.PROTECT, related_name="+", to="core.image"
                    ),
                ),
                ("media", models.ManyToManyField(blank=True, to="core.MediaItem")),
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
                ("text", models.TextField(help_text="The data in utf-8 encoded PEM text format.")),
                ("label", models.TextField(help_text="Human description of the PEM data.")),
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
                ("jws_signing_alg", models.TextField(help_text="The JWS-compatible signing algorithm.")),
                ("eligibility_types", models.ManyToManyField(to="core.EligibilityType")),
                (
                    "eligibility_verifier",
                    models.ForeignKey(on_delete=models.deletion.PROTECT, to="core.eligibilityverifier"),
                ),
                (
                    "payment_processor",
                    models.ForeignKey(on_delete=models.deletion.PROTECT, to="core.paymentprocessor"),
                ),
                (
                    "private_key",
                    models.ForeignKey(
                        help_text="The Agency's private key, used to sign tokens created on behalf of this Agency.",
                        on_delete=models.deletion.PROTECT,
                        related_name="+",
                        to="core.pemdata",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="paymentprocessor",
            name="client_cert",
            field=models.ForeignKey(
                help_text="The certificate used for client certificate authentication to the API.",
                on_delete=models.deletion.PROTECT,
                related_name="+",
                to="core.pemdata",
            ),
        ),
        migrations.AddField(
            model_name="paymentprocessor",
            name="client_cert_private_key",
            field=models.ForeignKey(
                help_text="The private key, used to sign the certificate.",
                on_delete=models.deletion.PROTECT,
                related_name="+",
                to="core.pemdata",
            ),
        ),
        migrations.AddField(
            model_name="paymentprocessor",
            name="client_cert_root_ca",
            field=models.ForeignKey(
                help_text="The root CA bundle, used to verify the server.",
                on_delete=models.deletion.PROTECT,
                related_name="+",
                to="core.pemdata",
            ),
        ),
        migrations.CreateModel(
            name="PageNavigation",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("target", models.ForeignKey(on_delete=models.deletion.PROTECT, related_name="+", to="core.page")),
                ("text", models.ForeignKey(on_delete=models.deletion.PROTECT, related_name="+", to="core.i18ntext")),
            ],
        ),
        migrations.AddField(
            model_name="page",
            name="navigation",
            field=models.ManyToManyField(blank=True, to="core.PageNavigation"),
        ),
        migrations.AddField(
            model_name="page",
            name="paragraphs",
            field=models.ManyToManyField(blank=True, to="core.I18nText"),
        ),
        migrations.AddField(
            model_name="page",
            name="title",
            field=models.ForeignKey(on_delete=models.deletion.PROTECT, related_name="+", to="core.i18ntext"),
        ),
        migrations.AddField(
            model_name="eligibilityverifier",
            name="public_key",
            field=models.ForeignKey(
                help_text="The Verifier's public key, used to encrypt requests targeted at this Verifier and to verify signed responses from this verifier.",  # noqa: 501
                on_delete=models.deletion.PROTECT,
                related_name="+",
                to="core.pemdata",
            ),
        ),
    ]
