# Generated by Django 3.0.7 on 2020-07-15 12:54

import web.apply.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('viewflow', '0008_jsonfield_and_artifact'),
        ('companies', '0002_auto_20200630_0949'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationProcess',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='viewflow.Process')),
                ('applicant_full_name', models.TextField(null=True)),
                ('event_name', models.TextField(null=True)),
                ('event_date', models.DateField(null=True, validators=[web.apply.models.is_in_future])),
                ('requested_amount', models.DecimalField(decimal_places=2, max_digits=6, null=True, validators=[django.core.validators.MinValueValidator(500), django.core.validators.MaxValueValidator(2500)])),
                ('approved', models.BooleanField(default=False)),
                ('approved_at', models.DateTimeField(null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='companies.Company')),
            ],
            options={
                'abstract': False,
            },
            bases=('viewflow.process',),
        ),
    ]
