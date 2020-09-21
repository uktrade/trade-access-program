# Generated by Django 3.0.7 on 2020-08-27 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grant_applications', '0006_auto_20200812_0941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grantapplication',
            name='number_of_employees',
            field=models.CharField(choices=[('fewer-than-10', 'Has Fewer Than 10'), ('10-to-49', 'Has 10 To 49'), ('50-to-249', 'Has 50 To 249'), ('250-or-more', 'Has 250 Or More')], max_length=20, null=True),
        ),
    ]