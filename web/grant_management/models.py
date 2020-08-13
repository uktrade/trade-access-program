from django.conf import settings
from django.db import models
from django.db.models import PROTECT
from viewflow.models import Process


class GrantManagementProcess(Process):
    DECISION_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]

    grant_application = models.OneToOneField(
        'grant_applications.GrantApplication', on_delete=PROTECT, null=True,
        related_name='grant_application_process'
    )
    employee_count_is_verified = models.BooleanField(null=True, choices=settings.BOOLEAN_CHOICES)
    turnover_is_verified = models.BooleanField(null=True, choices=settings.BOOLEAN_CHOICES)
    decision = models.CharField(null=True, choices=DECISION_CHOICES, max_length=10)
