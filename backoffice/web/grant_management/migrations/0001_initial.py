# Generated by Django 3.1.1 on 2020-10-13 15:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('grant_applications', '0001_initial'),
        ('viewflow', '0008_jsonfield_and_artifact'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrantManagementProcess',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='viewflow.process')),
                ('employee_count_is_verified', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], null=True)),
                ('turnover_is_verified', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], null=True)),
                ('decision', models.CharField(choices=[('approved', 'Approved'), ('rejected', 'Rejected')], max_length=10, null=True)),
                ('grant_application', models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='grant_management_process', to='grant_applications.grantapplication')),
            ],
            options={
                'abstract': False,
            },
            bases=('viewflow.process',),
        ),
    ]
