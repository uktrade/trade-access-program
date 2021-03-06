# Generated by Django 3.1.1 on 2020-10-13 15:41

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=500)),
                ('sector', models.CharField(max_length=500)),
                ('sub_sector', models.CharField(max_length=500)),
                ('city', models.CharField(max_length=500)),
                ('country', models.CharField(max_length=500)),
                ('start_date', models.DateField(max_length=500)),
                ('end_date', models.DateField(max_length=500)),
                ('show_type', models.CharField(choices=[('Physical', 'Physical')], max_length=500)),
                ('tcp', models.CharField(max_length=500)),
                ('tcp_website', models.CharField(max_length=500)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
