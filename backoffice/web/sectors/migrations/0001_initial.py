# Generated by Django 3.1.1 on 2020-10-13 15:41

from django.db import migrations, models
import uuid
import web.sectors.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('sector_code', models.CharField(max_length=6, validators=[web.sectors.models.sector_code_validator])),
                ('name', models.CharField(max_length=500)),
                ('cluster_name', models.CharField(max_length=500)),
                ('full_name', models.CharField(max_length=500)),
                ('sub_sector_name', models.CharField(max_length=500, null=True)),
                ('sub_sub_sector_name', models.CharField(max_length=500, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
