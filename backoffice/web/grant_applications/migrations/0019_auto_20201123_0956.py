# Generated by Django 3.1.1 on 2020-11-23 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grant_applications', '0018_auto_20201117_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stateaid',
            name='description',
            field=models.CharField(max_length=2000),
        ),
    ]
