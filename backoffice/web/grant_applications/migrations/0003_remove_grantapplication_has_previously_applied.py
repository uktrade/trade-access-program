# Generated by Django 3.1.1 on 2020-10-23 14:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grant_applications', '0002_auto_20201023_1311'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grantapplication',
            name='has_previously_applied',
        ),
    ]
