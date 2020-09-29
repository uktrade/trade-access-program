from web.grant_applications.services import BackofficeService


class UpdateBackofficeGrantApplicationMixin:

    def save(self, *args, **kwargs):
        if self.cleaned_data:
            BackofficeService().update_grant_application(
                grant_application_id=str(self.instance.backoffice_grant_application_id),
                **{k: v for k, v in self.cleaned_data.items() if v is not None}
            )
        return super().save(*args, **kwargs)
