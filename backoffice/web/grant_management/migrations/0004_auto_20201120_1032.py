# Generated by Django 3.1.1 on 2020-11-20 10:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grant_management', '0003_auto_20201120_0949'),
    ]

    operations = [
        migrations.AddField(
            model_name='grantmanagementprocess',
            name='export_strategy_justification',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='grantmanagementprocess',
            name='export_strategy_score',
            field=models.IntegerField(choices=[(1, '1 - Poor'), (2, '2 - Limited'), (3, '3 - Acceptable'), (4, '4 - Good'), (5, '5 - Excellent')], null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
    ]
