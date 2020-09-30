from django.http import HttpResponseRedirect
from django.urls import reverse

from web.grant_applications.services import BackofficeService


class BackofficeMixin:

    def get_object(self):
        obj = super().get_object()
        self.backoffice_service = BackofficeService()
        if obj.backoffice_grant_application_id:
            self.backoffice_grant_application = self.backoffice_service.get_grant_application(
                obj.backoffice_grant_application_id
            )
        return obj


class InitialDataMixin:

    def get_initial(self):
        initial = super().get_initial()
        if hasattr(self, 'backoffice_grant_application'):
            for field in self.form_class._meta.fields:
                if self.backoffice_grant_application.get(field) is not None:
                    initial[field] = self.backoffice_grant_application.get(field)
        return initial


class ConfirmationRedirectMixin:

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.sent_for_review:
            return HttpResponseRedirect(
                reverse('grant_applications:confirmation', args=(self.object.pk,))
            )
        return self.render_to_response(self.get_context_data())
