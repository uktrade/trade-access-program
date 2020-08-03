from django.db import models

from web.core.abstract_models import BaseMetaModel


class Event(BaseMetaModel):
    name = models.CharField(max_length=500)
    sector = models.CharField(max_length=500)
    sub_sector = models.CharField(max_length=500)
    city = models.CharField(max_length=500)
    country = models.CharField(max_length=500)
    start_date = models.DateField(max_length=500)
    end_date = models.DateField(max_length=500)
    show_type = models.CharField(max_length=500, choices=[('Physical', 'Physical')])
    tcp = models.CharField(max_length=500)
    tcp_website = models.CharField(max_length=500)

    @property
    def display_name(self):
        return f"{self.country} | {self.city} | {self.start_date.strftime('%d %b %Y')} | " \
               f"{self.sector} | {self.name}"
