# Generated by Django 3.1.1 on 2020-10-23 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grant_applications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grantapplication',
            name='search_term',
            field=models.CharField(max_length=500, null=True),
        ),
    ]