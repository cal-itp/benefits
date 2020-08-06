import uuid


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
                ('short_name', models.CharField(max_length=10)),
                ('long_name', models.CharField(max_length=25)),
                ('group_id', models.UUIDField(default=uuid.uuid4())),
            ],
        ),
        migrations.CreateModel(
            name='TransitAgency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=5)),
                ('long_name', models.CharField(max_length=25)),
                ('agency_id', models.CharField(max_length=50)),
                ('mechant_id', models.UUIDField(default=uuid.uuid4())),
                ('logo_url', models.URLField()),
                ('street_address1', models.CharField(max_length=25)),
                ('street_address2', models.CharField(max_length=25)),
                ('city', models.CharField(max_length=25)),
                ('zipcode', models.CharField(max_length=5)),
                ('eligibility_types', models.ManyToManyField(to='core.EligibilityType'))
            ],
        ),
    ]
