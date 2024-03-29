from django.forms import forms
from django.http import HttpResponseRedirect
from django.urls import reverse

from web.core.forms import FORM_MSGS
from web.grant_applications.services import BackofficeService, BackofficeServiceException


class BackofficeMixin:
    grant_application_fields = None

    def get_object(self):
        obj = super().get_object()
        self.backoffice_service = BackofficeService()
        if obj.backoffice_grant_application_id:
            try:
                self.backoffice_grant_application = self.backoffice_service.get_grant_application(
                    obj.backoffice_grant_application_id
                )
            except BackofficeServiceException:
                self.backoffice_grant_application = {
                    'id': obj.backoffice_grant_application_id
                }
        return obj

    def form_valid(self, form, extra_grant_application_data=None):
        if (form.cleaned_data or extra_grant_application_data) and form.instance.backoffice_grant_application_id:
            extra_grant_application_data = extra_grant_application_data or {}
            fields = self.grant_application_fields or form.cleaned_data.keys()
            grant_application_data = {f: form.cleaned_data[f] for f in fields}
            grant_application_data.update(extra_grant_application_data)
            if grant_application_data:
                try:
                    self.backoffice_grant_application = \
                        self.backoffice_service.update_grant_application(
                            grant_application_id=str(form.instance.backoffice_grant_application_id),
                            **grant_application_data
                        )
                except BackofficeServiceException:
                    form.add_error(None, forms.ValidationError(FORM_MSGS['resubmit']))
                    return super().form_invalid(form)
        return super().form_valid(form)


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
        response = super().get(request, *args, **kwargs)
        if self.backoffice_grant_application.get('sent_for_review', False):
            return HttpResponseRedirect(
                reverse('grant_applications:confirmation', args=(self.object.pk,))
            )
        return response


class IneligibleRedirectMixin:

    def _is_eligible(self):
        if self.object.has_viewed_review_page:
            return True
        elif not self.backoffice_grant_application.get('is_eligible', True):
            return False
        return True

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if not self._is_eligible():
            return HttpResponseRedirect(reverse('grant_applications:ineligible'))
        return response

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # First check if application data already set is ineligible
        if not self._is_eligible():
            return HttpResponseRedirect(reverse('grant_applications:ineligible'))

        response = super().post(request, *args, **kwargs)

        # After update is done check if application is now set to ineligible
        if not self._is_eligible():
            return HttpResponseRedirect(reverse('grant_applications:ineligible'))

        return response
