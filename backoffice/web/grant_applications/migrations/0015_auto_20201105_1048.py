# Generated by Django 3.1.1 on 2020-11-05 10:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grant_applications', '0014_auto_20201104_1132'),
    ]

    operations = [
        migrations.AddField(
            model_name='grantapplication',
            name='company_name',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='grantapplication',
            name='company_postcode',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='grantapplication',
            name='company_type',
            field=models.CharField(choices=[('limited company', 'Limited company'), ('partnership', 'Partnership'), ('sole trader', 'Sole trader'), ('other', 'Other e.g. charity, university, publicly funded body')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='grantapplication',
            name='manual_registration_number',
            field=models.CharField(max_length=10, null=True, validators=[django.core.validators.RegexValidator(regex='(SC|NI|[0-9]{2})[0-9]{6}')]),
        ),
        migrations.AddField(
            model_name='grantapplication',
            name='manual_vat_number',
            field=models.CharField(max_length=10, null=True, validators=[django.core.validators.RegexValidator(regex='([0-9]{9}([0-9]{3})?|[A-Z]{2}[0-9]{3})')]),
        ),
        migrations.AddField(
            model_name='grantapplication',
            name='time_trading_in_uk',
            field=models.CharField(choices=[('less than 1 year', 'Less than 1 year'), ('2 to 5 years', '2 to 5 years'), ('6 to 10 years', '6 to 10 years'), ('more than 10 years', 'More than 10 years')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='grantapplication',
            name='website',
            field=models.URLField(max_length=500, null=True),
        ),
    ]
