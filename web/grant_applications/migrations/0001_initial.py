# Generated by Django 3.0.7 on 2020-07-30 08:54

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GrantApplication',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('duns_number', models.IntegerField()),
                ('applicant_full_name', models.CharField(max_length=500, null=True)),
                ('applicant_email', models.EmailField(max_length=254, null=True)),
                ('event', models.TextField(null=True)),
                ('is_already_committed_to_event', models.BooleanField(null=True)),
                ('is_intending_on_other_financial_support', models.BooleanField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]