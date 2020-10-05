from web.grant_applications.services import BackofficeService


class UpdateBackofficeGrantApplicationMixin:
    grant_application_fields = None

    def save(self, *args, **kwargs):
        if self.cleaned_data:
            fields = self.grant_application_fields or self.cleaned_data.keys()
            BackofficeService().update_grant_application(
                grant_application_id=str(self.instance.backoffice_grant_application_id),
                **{f: self.cleaned_data[f] for f in fields if self.cleaned_data[f] is not None}
            )
        return super().save(*args, **kwargs)


class FormatLabelMixin:

    def format_label(self, field_name, **kwargs):
        self[field_name].label = self[field_name].label.format(**kwargs)
