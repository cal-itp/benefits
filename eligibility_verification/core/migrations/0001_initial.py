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
                ('name', models.CharField(max_length=25)),
                ('label', models.CharField(max_length=50)),
                ('group_id', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='EligibilityVerifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('api_url', models.CharField(max_length=50)),
                ('eligibility_types', models.ManyToManyField(to='core.EligibilityType')),
            ],
        ),
        migrations.CreateModel(
            name='TransitAgency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=5)),
                ('long_name', models.CharField(max_length=50)),
                ('agency_id', models.CharField(max_length=50)),
                ('mechant_id', models.CharField(max_length=50)),
                ('logo_url', models.URLField()),
                ('street_address1', models.CharField(max_length=50)),
                ('street_address2', models.CharField(max_length=50, blank=True)),
                ('city', models.CharField(max_length=50)),
                ('zipcode', models.CharField(max_length=5)),
                ('active', models.BooleanField(default=False)),
                ('eligibility_types', models.ManyToManyField(to='core.EligibilityType')),
                ('eligibility_verifiers', models.ManyToManyField(to='core.EligibilityVerifier'))
            ],
        ),
    ]
