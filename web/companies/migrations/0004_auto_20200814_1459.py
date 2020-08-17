# Generated by Django 3.0.7 on 2020-08-14 14:59

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_auto_20200813_1528'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'verbose_name_plural': 'companies'},
        ),
        migrations.RemoveField(
            model_name='company',
            name='dnb_service_duns_number',
        ),
        migrations.AddField(
            model_name='company',
            name='duns_number',
            field=models.IntegerField(default=0, unique=True),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='DnbGetCompanyResponse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='companies.Company')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
