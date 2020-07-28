from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import PROTECT
from django.utils.datetime_safe import date
from viewflow.models import Process


def is_in_future(value):
    if value <= date.today():
        raise ValidationError('Event date must be in the future.')


class ApplicationProcess(Process):
    company = models.ForeignKey('companies.Company', on_delete=PROTECT, null=True)

    applicant_full_name = models.TextField(null=True)
    applicant_email = models.EmailField(null=True)
    event_name = models.TextField(null=True)
    event_date = models.DateField(null=True, validators=[is_in_future])
    requested_amount = models.DecimalField(
        null=True,
        validators=[
            MinValueValidator(settings.MIN_GRANT_VALUE),
            MaxValueValidator(settings.MAX_GRANT_VALUE)
        ],
        **settings.GRANT_VALUE_DECIMAL_PRECISION
    )

    approved = models.BooleanField(default=False)
