from uuid import uuid4

from django.db import models


class GrantApplicationLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    backoffice_grant_application_id = models.UUIDField(unique=True)
    has_viewed_review_page = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(editable=False, auto_now_add=True)
