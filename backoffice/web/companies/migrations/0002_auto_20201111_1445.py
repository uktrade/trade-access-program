# Generated by Django 3.1.1 on 2020-11-11 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='registration_number',
            field=models.CharField(max_length=20, null=True, unique=True),
        ),
    ]
