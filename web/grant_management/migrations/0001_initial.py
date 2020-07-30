# Generated by Django 3.0.7 on 2020-07-30 08:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('viewflow', '0008_jsonfield_and_artifact'),
        ('grant_applications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrantApplicationProcess',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='viewflow.Process')),
                ('approved', models.BooleanField(default=False)),
                ('grant_application', models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, to='grant_applications.GrantApplication')),
            ],
            options={
                'abstract': False,
            },
            bases=('viewflow.process',),
        ),
    ]
