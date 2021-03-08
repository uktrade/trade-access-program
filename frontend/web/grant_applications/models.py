from uuid import uuid4

from django.db import models
from django.urls import reverse, NoReverseMatch


class GrantApplicationLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    backoffice_grant_application_id = models.UUIDField(unique=True)
    has_viewed_review_page = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    state_url_name = models.CharField(max_length=255, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(editable=False, auto_now_add=True)

    APPLICATION_FIRST_STEP_URL_NAME = 'grant_applications:previous-applications'

    @property
    def state_url(self):
        first_step_url = reverse(self.APPLICATION_FIRST_STEP_URL_NAME, args=(self.id,))
        if self.state_url_name:
            try:
                return reverse(self.state_url_name, args=(self.id, ))
            except NoReverseMatch:
                return first_step_url
        return first_step_url
