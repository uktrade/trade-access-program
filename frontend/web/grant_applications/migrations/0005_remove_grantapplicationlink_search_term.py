# Generated by Django 3.1.1 on 2020-10-23 13:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grant_applications', '0004_auto_20201008_0824'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grantapplicationlink',
            name='search_term',
        ),
    ]
