# Generated by Django 3.0.7 on 2020-09-01 12:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('grant_applications', '0011_sector_transfer_to_fk'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grantapplication',
            name='sector',
        ),
        migrations.RenameField(
            model_name='grantapplication',
            old_name='sector_transfer',
            new_name='sector'
        ),
    ]
