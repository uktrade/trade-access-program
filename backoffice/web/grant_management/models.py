from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import PROTECT
from viewflow.models import Process


class GrantManagementProcess(Process):

    class ScoreChoices(models.IntegerChoices):
        ONE = 1, '1 - Poor'
        TWO = 2, '2 - Limited'
        THREE = 3, '3 - Acceptable'
        FOUR = 4, '4 - Good'
        FIVE = 5, '5 - Excellent'

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
    products_and_services_score = models.IntegerField(
        null=True, choices=ScoreChoices.choices,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    products_and_services_justification = models.TextField(null=True)
    products_and_services_competitors_score = models.IntegerField(
        null=True, choices=ScoreChoices.choices,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    products_and_services_competitors_justification = models.TextField(null=True)
    export_strategy_score = models.IntegerField(
        null=True, choices=ScoreChoices.choices,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    export_strategy_justification = models.TextField(null=True)
    event_is_appropriate = models.BooleanField(
        null=True, choices=settings.BOOLEAN_CHOICES
    )
    decision = models.CharField(null=True, choices=Decision.choices, max_length=10)

    @property
    def is_approved(self):
        return self.decision == self.Decision.APPROVED

    @property
    def is_rejected(self):
        return self.decision == self.Decision.REJECTED

    @property
    def total_verified(self):
        return sum([
            self.previous_applications_is_verified,
            self.event_commitment_is_verified,
            self.business_entity_is_verified,
            self.state_aid_is_verified
        ])

    @property
    def suitability_score(self):
        return sum([
            self.products_and_services_score,
            self.products_and_services_competitors_score,
            self.export_strategy_score
        ])
