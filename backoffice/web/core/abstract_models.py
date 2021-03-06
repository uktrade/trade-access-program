from uuid import uuid4

from django.db import models


class BaseMetaModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(editable=False, auto_now_add=True)

    @property
    def id_str(self):
        return str(self.id)

    class Meta:
        abstract = True
