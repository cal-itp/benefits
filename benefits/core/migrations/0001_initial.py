from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountProvider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('api_base_url', models.TextField()),
                ('api_access_token_endpoint', models.TextField()),
                ('api_access_token_request_key', models.TextField()),
                ('api_access_token_request_val', models.TextField()),
                ('card_tokenize_url', models.TextField()),
                ('card_tokenize_func', models.TextField()),
                ('card_tokenize_env', models.TextField()),
                ('client_cert_pem', models.TextField(help_text="A certificate in PEM format, used for client certificate authentication to this Provider's API.")),
                ('client_cert_private_key_pem', models.TextField(help_text="The private key in PEM format used to sign the certificate.")),
                ('client_cert_root_ca_pem', models.TextField(help_text="The root CA bundle in PEM format used to verify the Provider's server.")),
            ],
        ),
        migrations.CreateModel(
            name='EligibilityType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('label', models.TextField()),
                ('group_id', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='EligibilityVerifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('api_url', models.TextField()),
                ('api_auth_header', models.TextField()),
                ('api_auth_key', models.TextField()),
                ('public_key_pem', models.TextField(help_text="The Verifier's public key in PEM format, used to encrypt requests targeted at this Verifier and to verify signed responses from this verifier.")),
                ('jwe_cek_enc', models.TextField(help_text='The JWE-compatible Content Encryption Key (CEK) key-length and mode')),
                ('jwe_encryption_alg', models.TextField(help_text='The JWE-compatible encryption algorithm')),
                ('jws_signing_alg', models.TextField(help_text='The JWS-compatible signing algorithm')),
                ('eligibility_types', models.ManyToManyField(to='core.EligibilityType')),
            ],
        ),
        migrations.CreateModel(
            name='TransitAgency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.TextField()),
                ('short_name', models.TextField()),
                ('long_name', models.TextField()),
                ('agency_id', models.TextField()),
                ('private_key_pem', models.TextField(help_text="The Agency's private key in PEM format, used to sign tokens created on behalf of this Agency.")),
                ('jws_signing_alg', models.TextField(help_text='The JWS-compatible signing algorithm.')),
                ('merchant_id', models.TextField()),
                ('logo_url', models.URLField()),
                ('street_address1', models.TextField()),
                ('street_address2', models.TextField(blank=True)),
                ('city', models.TextField()),
                ('zip_code', models.TextField()),
                ('country_code', models.TextField()),
                ('phone', models.TextField()),
                ('active', models.BooleanField(default=False)),
                ('eligibility_types', models.ManyToManyField(to='core.EligibilityType')),
                ('eligibility_verifiers', models.ManyToManyField(to='core.EligibilityVerifier')),
                ('discount_provider', models.ForeignKey(on_delete=models.deletion.PROTECT, to='core.DiscountProvider'))
            ],
        ),
    ]
