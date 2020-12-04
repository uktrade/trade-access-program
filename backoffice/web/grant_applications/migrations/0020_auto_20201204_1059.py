# Generated by Django 3.1.1 on 2020-12-04 10:59

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grant_applications', '0019_auto_20201123_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grantapplication',
            name='export_regions',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('africa', 'Africa'), ('asia pacific', 'Asia-Pacific'), ('china', 'China'), ('eastern europe and central asia', 'Eastern Europe and Central Asia'), ('europe', 'Europe'), ('latin america', 'Latin America'), ('middle east', 'Middle East'), ('north america', 'North America'), ('south asia', 'South Asia')], max_length=50), null=True, size=None),
        ),
    ]