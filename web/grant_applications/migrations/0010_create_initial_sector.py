# Generated by Django 3.0.7 on 2020-09-01 12:37

from django.db import migrations


def create_sector(apps, schema_editor):
    Sector = apps.get_model('grant_applications', 'Sector')
    Sector.objects.create(pk='7bd59944-2468-4669-a307-619ff9d083e2', name='Unknown')


def create_sector_reverse(apps, schema_editor):
    Sector = apps.get_model('grant_applications', 'Sector')
    sector = Sector.objects.get(pk='7bd59944-2468-4669-a307-619ff9d083e2')
    sector.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('grant_applications', '0009_auto_20200901_1223'),
    ]

    operations = [
        migrations.RunPython(create_sector, create_sector_reverse),
    ]
