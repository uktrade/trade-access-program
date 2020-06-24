from django.db import models

from api.core.abstract_models import BaseMetaModel


class Company(BaseMetaModel):
    registration_number = models.IntegerField(unique=True)
