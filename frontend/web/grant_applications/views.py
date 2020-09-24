from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView, TemplateView

from web.core.view_mixins import PageContextMixin, SuccessUrlObjectPkMixin, BackContextMixin
from web.grant_applications.forms import (
    SearchCompanyForm, SelectCompanyForm, AboutYourBusinessForm, AboutYouForm, AboutTheEventForm,
    PreviousApplicationsForm, EventIntentionForm, BusinessInformationForm, ExportExperienceForm,
    StateAidForm, ApplicationReviewForm
)
from web.grant_applications.models import GrantApplicationLink
from web.grant_applications.services import BackofficeService, generate_grant_application_summary, \
    BackofficeServiceException


class BackofficeMixin:

    def get_object(self):
        obj = super().get_object()
        self.backoffice_service = BackofficeService()
        self.backoffice_grant_application = self.backoffice_service.get_grant_application(
            obj.backoffice_grant_application_id
        )
        return obj


class InitialDataMixin:

    def get_initial(self):
        initial = super().get_initial()
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


class SearchCompanyView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin, CreateView):
    form_class = SearchCompanyForm
    template_name = 'grant_applications/eligibility_form_page.html'
    success_url_name = 'grant-applications:select-company'
    page = {
        'heading': _('Search for your company')
    }

    def get_back_url(self):
        return reverse('grant-applications:index')


class SelectCompanyView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                        ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = SelectCompanyForm
    template_name = 'grant_applications/generic_form_page.html'
    success_url_name = 'grant-applications:about-your-business'
    page = {
        'heading': _('Select your company')
    }

    def get_back_url(self):
        return reverse('grant-applications:search-company')


class AboutYourBusinessView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                            BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin,
                            UpdateView):
    model = GrantApplicationLink
    form_class = AboutYourBusinessForm
    template_name = 'grant_applications/about_your_business.html'
    success_url_name = 'grant-applications:about-you'
    back_url_name = 'grant-applications:select-company'
    page = {
        'heading': _('About your business')
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.backoffice_grant_application['company']:
            context['table'] = [
                {
                    'label': 'Dun and Bradstreet Number',
                    'value': self.backoffice_grant_application['company']['duns_number']
                },
                {
                    'label': 'Company Name',
                    'value': self.backoffice_grant_application['company']['name']
                },
                {
                    'label': 'Previous Applications',
                    'value': self.backoffice_grant_application['company']['previous_applications']
                },
                {
                    'label': 'Applications in Review',
                    'value': self.backoffice_grant_application['company']['applications_in_review']
                },
            ]
        return context


class AboutYouView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin, BackofficeMixin,
                   InitialDataMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = AboutYouForm
    template_name = 'grant_applications/generic_form_page.html'
    success_url_name = 'grant_applications:about-the-event'
    back_url_name = 'grant-applications:about-your-business'
    page = {
        'heading': _('About you')
    }


class AboutTheEventView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                        BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = AboutTheEventForm
    template_name = 'grant_applications/generic_form_page.html'
    success_url_name = 'grant_applications:previous-applications'
    back_url_name = 'grant-applications:about-you'
    page = {
        'heading': _('What event are you intending to exhibit at?')
    }


class PreviousApplicationsView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                               InitialDataMixin, BackofficeMixin, UpdateView):
    model = GrantApplicationLink
    form_class = PreviousApplicationsForm
    template_name = 'grant_applications/previous_applications.html'
    success_url_name = 'grant_applications:event-intention'
    back_url_name = 'grant-applications:about-the-event'
    page = {
        'heading': _('Your application')
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            if kwargs['data'].get('has_previously_applied') == 'True':
                kwargs['data'] = {
                    'has_previously_applied': True,
                    'previous_applications': 0
                }
        return kwargs


class EventIntentionView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                         BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = EventIntentionForm
    template_name = 'grant_applications/event_intention.html'
    success_url_name = 'grant_applications:business-information'
    back_url_name = 'grant-applications:previous-applications'
    page = {
        'heading': _('Your application')
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'].format_label(
            field_name='is_first_exhibit_at_event',
            event_name=self.backoffice_grant_application['event']['name']
        )
        context['form'].format_label(
            field_name='number_of_times_exhibited_at_event',
            event_name=self.backoffice_grant_application['event']['name']
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            if kwargs['data'].get('is_first_exhibit_at_event') == 'True':
                kwargs['data'] = {
                    'is_first_exhibit_at_event': True,
                    'number_of_times_exhibited_at_event': 0
                }
        return kwargs


class BusinessInformationView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                              InitialDataMixin, ConfirmationRedirectMixin, BackofficeMixin,
                              UpdateView):
    model = GrantApplicationLink
    form_class = BusinessInformationForm
    template_name = 'grant_applications/generic_form_page.html'
    success_url_name = 'grant_applications:export-experience'
    back_url_name = 'grant-applications:event-intention'
    page = {
        'heading': _('About your business')
    }

    def get_initial(self):
        initial = super().get_initial()
        company_data = self.backoffice_grant_application['company']

        if not self.backoffice_grant_application['business_name_at_exhibit']:
            initial['business_name_at_exhibit'] = company_data['name']

        if not self.backoffice_grant_application['turnover']:
            initial['turnover'] = int(
                company_data['last_dnb_get_company_response']['data']['annual_sales']
            )

        if not self.backoffice_grant_application['number_of_employees']:
            initial['number_of_employees'] = self.form_class.NumberOfEmployees.get_choice_by_number(
                company_data['last_dnb_get_company_response']['data']['employee_number']
            )

        if not self.backoffice_grant_application['website']:
            initial['website'] = company_data['last_dnb_get_company_response']['data']['domain']

        return initial


class ExportExperienceView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                           BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin,
                           UpdateView):
    model = GrantApplicationLink
    form_class = ExportExperienceForm
    template_name = 'grant_applications/generic_form_page.html'
    back_url_name = 'grant-applications:business-information'
    success_url_name = 'grant_applications:state-aid'
    page = {
        'heading': _('About your export experience')
    }


class StateAidView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin, BackofficeMixin,
                   InitialDataMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = StateAidForm
    template_name = 'grant_applications/state_aid.html'
    back_url_name = 'grant-applications:export-experience'
    success_url_name = 'grant_applications:application-review'
    page = {
        'heading': _('State aid restrictions')
    }


class ApplicationReviewView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                            BackofficeMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = ApplicationReviewForm
    template_name = 'grant_applications/application_review.html'
    back_url_name = 'grant-applications:state-aid'
    success_url_name = 'grant_applications:confirmation'
    page = {
        'heading': _('Review your application'),
        'form_button_text': _('Accept and send'),
    }
    grant_application_flow = [
        SelectCompanyView,
        AboutYourBusinessView,
        AboutYouView,
        AboutTheEventView,
        PreviousApplicationsView,
        EventIntentionView,
        BusinessInformationView,
        ExportExperienceView,
        StateAidView,
    ]

    def generate_application_summary(self):
        application_summary = []

        url = SearchCompanyView(object=self.object).get_success_url()

        for view_class in self.grant_application_flow:
            summary = generate_grant_application_summary(
                form_class=view_class.form_class, url=url,
                grant_application=self.object
            )
            if summary:
                application_summary.append({
                    'heading': str(view_class.page.get('heading', '')),
                    'summary': summary
                })
            url = view_class(object=self.object).get_success_url()

        return application_summary

    def get_context_data(self, **kwargs):
        kwargs['application_summary'] = self.generate_application_summary()
        self.request.session['application_summary'] = kwargs['application_summary']
        return super().get_context_data(**kwargs)

    def try_send_grant_application_for_review(self, form):
        try:
            self.backoffice_service.send_grant_application_for_review(
                str(self.object.backoffice_grant_application_id),
                application_summary=self.request.session['application_summary']
            )
        except BackofficeServiceException:
            msg = forms.ValidationError('An unexpected error occurred. Please resubmit the form.')
            form.add_error(None, msg)
        else:
            self.object.sent_for_review = True

        return form

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        self.try_send_grant_application_for_review(form)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ConfirmationView(PageContextMixin, TemplateView):
    template_name = 'grant_applications/confirmation.html'
    page = {
        'panel_title': _('Application complete'),
        'panel_ref_text': _('Your reference number'),
        'confirmation_email_text': _('We have sent you a confirmation email.'),
        'next_steps_heading': _('What happens next'),
        'next_steps_line_1': _("We've sent your application to the Trade Access Program team."),
        'next_steps_line_2': _('They will contact you either to confirm your registration, or '
                               'to ask for more information.'),
    }
