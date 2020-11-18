from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
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
                ('public_key_pem', models.TextField()),
                ('jwe_cek_enc', models.TextField()),
                ('jwe_encryption_alg', models.TextField()),
                ('jws_signing_alg', models.TextField()),
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
                ('private_key_pem', models.TextField()),
                ('jws_signing_alg', models.TextField()),
                ('mechant_id', models.TextField()),
                ('logo_url', models.URLField()),
                ('street_address1', models.TextField()),
                ('street_address2', models.TextField(blank=True)),
                ('city', models.TextField()),
                ('zipcode', models.TextField()),
                ('phone', models.TextField()),
                ('active', models.BooleanField(default=False)),
                ('eligibility_types', models.ManyToManyField(to='core.EligibilityType')),
                ('eligibility_verifiers', models.ManyToManyField(to='core.EligibilityVerifier'))
            ],
        ),
    ]
