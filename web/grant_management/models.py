from django.conf import settings
from django.db import models
from django.db.models import PROTECT
from viewflow.models import Process


class GrantManagementProcess(Process):

    class Decision(models.TextChoices):
        APPROVED = 'approved'
        REJECTED = 'rejected'

    grant_application = models.OneToOneField(
        'grant_applications.GrantApplication', on_delete=PROTECT, null=True,
        related_name='grant_application_process'
    )
    employee_count_is_verified = models.BooleanField(null=True, choices=settings.BOOLEAN_CHOICES)
    turnover_is_verified = models.BooleanField(null=True, choices=settings.BOOLEAN_CHOICES)
    decision = models.CharField(null=True, choices=Decision.choices, max_length=10)

    @property
    def is_approved(self):
        return self.decision == self.Decision.APPROVED

    @property
    def is_rejected(self):
        return self.decision == self.Decision.REJECTED
