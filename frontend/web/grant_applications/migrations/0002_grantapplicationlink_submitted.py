# Generated by Django 3.0.7 on 2020-09-14 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grant_applications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='grantapplicationlink',
            name='submitted',
            field=models.BooleanField(default=False),
        ),
    ]
