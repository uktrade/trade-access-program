from django.db import transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, CreateView
from django.views.generic.base import TemplateView

from web.companies.services import DnbServiceClient
from web.core.exceptions import DnbServiceClientException
from web.core.view_mixins import PageContextMixin, SuccessUrlObjectPkMixin
from web.grant_applications.forms import (
    SearchCompanyForm, SelectCompanyForm, AboutYouForm,
    AboutTheEventForm, PreviousApplicationsForm, EventIntentionForm, BusinessInformationForm,
    StateAidForm, ExportExperienceForm, AboutYourBusinessForm, ApplicationReviewForm
)
from web.grant_applications.models import GrantApplication
from web.grant_applications.serializers import AboutYourBusinessTableSerializer
from web.grant_applications.services import generate_summary_of_form_fields
from web.grant_management.flows import GrantManagementFlow


def _get_company_select_choices(search_term):
    client = DnbServiceClient()

    try:
        companies = client.search_companies(search_term=search_term)
        searched_choices = [(c['duns_number'], c['primary_name']) for c in companies]
    except DnbServiceClientException:
        searched_choices = []

    choices = [('', 'Select your company...'), ('0', 'Company not listed')]
    choices[1:1] = searched_choices

    return choices


class SearchCompanyView(PageContextMixin, SuccessUrlObjectPkMixin, CreateView):
    form_class = SearchCompanyForm
    template_name = 'grant_applications/generic_form_page.html'
    success_url_name = 'grant_applications:select-company'
    page = {
        'heading': _('Search for your company')
    }


class SelectCompanyView(PageContextMixin, SuccessUrlObjectPkMixin, UpdateView):
    model = GrantApplication
    form_class = SelectCompanyForm
    template_name = 'grant_applications/generic_form_page.html'
    success_url_name = 'grant_applications:about-your-business'
    page = {
        'heading': _('Select your company')
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_choices'] = _get_company_select_choices(search_term=self.object.search_term)
        return kwargs


class AboutYourBusinessView(PageContextMixin, SuccessUrlObjectPkMixin, UpdateView):
    model = GrantApplication
    form_class = AboutYourBusinessForm
    template_name = 'grant_applications/about_your_business.html'
    success_url_name = 'grant_applications:about-you'
    page = {
        'heading': _('About your business')
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        serializer = AboutYourBusinessTableSerializer(instance=self.object.company)
        context['table'] = [{
            'label': serializer.fields[key].label,
            'value': value
            } for key, value in serializer.data.items()]
        return context


class AboutYouView(PageContextMixin, SuccessUrlObjectPkMixin, UpdateView):
    model = GrantApplication
    form_class = AboutYouForm
    template_name = 'grant_applications/generic_form_page.html'
    success_url_name = 'grant_applications:about-the-event'
    page = {
        'heading': _('About you')
    }


class AboutTheEventView(PageContextMixin, SuccessUrlObjectPkMixin, UpdateView):
    model = GrantApplication
    form_class = AboutTheEventForm
    template_name = 'grant_applications/generic_form_page.html'
    success_url_name = 'grant_applications:previous-applications'
    page = {
        'heading': _('What event are you intending to exhibit at?')
    }


class PreviousApplicationsView(PageContextMixin, SuccessUrlObjectPkMixin, UpdateView):
    model = GrantApplication
    form_class = PreviousApplicationsForm
    template_name = 'grant_applications/previous_applications.html'
    success_url_name = 'grant_applications:event-intention'
    page = {
        'heading': _('Your application')
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            if kwargs['data'].get('has_previously_applied') == 'False':
                kwargs['data'] = {
                    'has_previously_applied': False,
                    'previous_applications': 0
                }
        return kwargs


class EventIntentionView(PageContextMixin, SuccessUrlObjectPkMixin, UpdateView):
    model = GrantApplication
    form_class = EventIntentionForm
    template_name = 'grant_applications/event_intention.html'
    success_url_name = 'grant_applications:business-information'
    page = {
        'heading': _('Your application')
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'].format_label(
            field_name='is_first_exhibit_at_event',
            event=self.object.event
        )
        context['form'].format_label(
            field_name='number_of_times_exhibited_at_event',
            event=self.object.event
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


class BusinessInformationView(PageContextMixin, SuccessUrlObjectPkMixin, UpdateView):
    model = GrantApplication
    form_class = BusinessInformationForm
    template_name = 'grant_applications/generic_form_page.html'
    success_url_name = 'grant_applications:export-experience'
    page = {
        'heading': _('About your business')
    }

    def get_initial(self):
        initial = super().get_initial()
        if self.object.company.last_dnb_get_company_response:
            if not self.object.turnover:
                initial['turnover'] = self.object.company.last_dnb_get_company_response.data.get(
                    'annual_sales'
                )

            if not self.object.website:
                initial['website'] = self.object.company.last_dnb_get_company_response.data.get(
                    'domain'
                )

        return initial


class ExportExperienceView(PageContextMixin, SuccessUrlObjectPkMixin, UpdateView):
    model = GrantApplication
    form_class = ExportExperienceForm
    template_name = 'grant_applications/generic_form_page.html'
    success_url_name = 'grant_applications:state-aid'
    page = {
        'heading': _('About your export experience')
    }


class StateAidView(PageContextMixin, SuccessUrlObjectPkMixin, UpdateView):
    model = GrantApplication
    form_class = StateAidForm
    template_name = 'grant_applications/generic_form_page.html'
    success_url_name = 'grant_applications:application-review'
    page = {
        'heading': _('State aid restrictions')
    }


class ApplicationReviewView(PageContextMixin, SuccessUrlObjectPkMixin, UpdateView):
    model = GrantApplication
    form_class = ApplicationReviewForm
    template_name = 'grant_applications/application_review.html'
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

    def get_success_url(self):
        return reverse(
            'grant_applications:confirmation',
            kwargs={
                'pk': self.object.pk,
                'process_pk': self.process.pk,
            }
        )

    def generate_application_summary(self, grant_application=None):
        application_summary = []

        next_url = SearchCompanyView(object=self.object).get_success_url()

        for view_class in self.grant_application_flow:
            summary = generate_summary_of_form_fields(
                form_class=view_class.form_class,
                url=next_url,
                grant_application=grant_application or self.object
            )
            if summary:
                application_summary.append({
                    'heading': str(view_class.page.get('heading', '')),
                    'summary': summary
                })
            next_url = view_class(object=grant_application or self.object).get_success_url()

        return application_summary

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application_summary'] = self.generate_application_summary()
        self.request.session['application_summary'] = context['application_summary']
        return context

    def form_valid(self, form):
        with transaction.atomic():
            self.object.application_summary = self.request.session['application_summary']
            self.object.save()
            self.process = GrantManagementFlow.start.run(grant_application=self.object)
        return super().form_valid(form)


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
