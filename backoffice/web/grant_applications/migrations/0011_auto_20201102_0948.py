# Generated by Django 3.1.1 on 2020-11-02 09:48

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('grant_applications', '0010_auto_20201030_1553'),
    ]

    operations = [
        migrations.RenameField(
            model_name='grantapplication',
            old_name='in_contact_with_dit_trade_advisor',
            new_name='is_in_contact_with_dit_trade_advisor',
        ),
        migrations.RemoveField(
            model_name='grantapplication',
            name='is_first_exhibit_at_event',
        ),
        migrations.RemoveField(
            model_name='grantapplication',
            name='number_of_times_exhibited_at_event',
        ),
        migrations.AddField(
            model_name='grantapplication',
            name='additional_guidance',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='grantapplication',
            name='interest_in_event_description',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='grantapplication',
            name='is_in_contact_with_tcp',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='grantapplication',
            name='is_intending_to_exhibit_as_tcp_stand',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='grantapplication',
            name='stand_trade_name',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='grantapplication',
            name='tcp_email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='grantapplication',
            name='tcp_mobile_number',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, null=True, region='GB'),
        ),
        migrations.AddField(
            model_name='grantapplication',
            name='tcp_name',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='grantapplication',
            name='trade_show_experience_description',
            field=models.TextField(null=True),
        ),
    ]
