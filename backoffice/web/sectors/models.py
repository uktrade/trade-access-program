from django.db import models
from rest_framework.exceptions import ValidationError

from web.core.abstract_models import BaseMetaModel


def sector_code_validator(value):
    _raise = False

    if value[:2] != 'SL':
        _raise = True

    try:
        int(value[2:])
    except ValueError:
        _raise = True

    if _raise:
        raise ValidationError(f'{value} must have format SL0000')


class Sector(BaseMetaModel):
    sector_code = models.CharField(max_length=6, validators=[sector_code_validator])
    name = models.CharField(max_length=500)
    cluster_name = models.CharField(max_length=500)
    full_name = models.CharField(max_length=500)
    sub_sector_name = models.CharField(max_length=500, null=True)
    sub_sub_sector_name = models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.full_name
