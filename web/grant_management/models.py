from django.db import models
from django.db.models import PROTECT
from viewflow.models import Process


class GrantManagementProcess(Process):
    grant_application = models.OneToOneField(
        'grant_applications.GrantApplication', on_delete=PROTECT, null=True,
        related_name='grant_application_process'
    )
    acknowledge_application = models.BooleanField(default=False)
    employee_count_is_verified = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
