from django.db import models
from django.db.models import PROTECT
from viewflow.models import Process


class GrantManagementProcess(Process):

    class VerifyChoices(models.TextChoices):
        CONFIRM = True, 'Confirm'
        CHALLENGE = False, 'Challenge'

    class Decision(models.TextChoices):
        APPROVED = 'approved'
        REJECTED = 'rejected'

    grant_application = models.OneToOneField(
        'grant_applications.GrantApplication', on_delete=PROTECT, null=True,
        related_name='grant_management_process'
    )
    previous_applications_is_verified = models.BooleanField(null=True)
    event_commitment_is_verified = models.BooleanField(null=True)
    business_entity_is_verified = models.BooleanField(null=True)
    state_aid_is_verified = models.BooleanField(null=True)
    decision = models.CharField(null=True, choices=Decision.choices, max_length=10)

    @property
    def is_approved(self):
        return self.decision == self.Decision.APPROVED

    @property
    def is_rejected(self):
        return self.decision == self.Decision.REJECTED
