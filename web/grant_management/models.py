from django.db import models
from django.db.models import PROTECT
from viewflow.models import Process


class GrantApplicationProcess(Process):
    grant_application = models.OneToOneField(
        'grant_applications.GrantApplication', on_delete=PROTECT, null=True
    )
    approved = models.BooleanField(default=False)
