# Generated by Django 3.1.1 on 2020-11-20 14:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grant_management', '0004_auto_20201120_1032'),
    ]

    operations = [
        migrations.AddField(
            model_name='grantmanagementprocess',
            name='event_is_appropriate',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], null=True),
        ),
        migrations.AddField(
            model_name='grantmanagementprocess',
            name='products_and_services_competitors_justification',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='grantmanagementprocess',
            name='products_and_services_competitors_score',
            field=models.IntegerField(choices=[(1, '1 - Poor'), (2, '2 - Limited'), (3, '3 - Acceptable'), (4, '4 - Good'), (5, '5 - Excellent')], null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
    ]
