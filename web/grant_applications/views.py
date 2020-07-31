from django.forms import models as model_forms
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, UpdateView, CreateView
from django.views.generic.base import TemplateView

from web.companies.services import DnbServiceClient
from web.core.exceptions import DnbServiceClientException
from web.core.view_mixins import PageContextMixin, SuccessUrlObjectPkMixin
from web.grant_applications.forms import SearchCompanyForm, SelectCompanyForm, AboutYouForm, \
    AboutTheEventForm, PreviousApplicationsForm, EventIntentionForm, BusinessInformationForm, \
    StateAidForm
from web.grant_applications.models import GrantApplication
from web.grant_management.flows import GrantApplicationFlow


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


class SearchCompanyView(PageContextMixin, FormView):
    form_class = SearchCompanyForm
    template_name = 'grant_applications/generic_form_page.html'
    page = {
        'heading': _('Search for your company')
    }

    def get_success_url(self):
        return reverse('grant_applications:select-company') + f'?{urlencode(self.extra_context)}'

    def form_valid(self, form):
        self.request.session['search_term'] = form.cleaned_data['search_term']
        self.extra_context = {'search_term': form.cleaned_data['search_term']}
        return super().form_valid(form)


class SelectCompanyView(PageContextMixin, SuccessUrlObjectPkMixin, CreateView):
    form_class = SelectCompanyForm
    template_name = 'grant_applications/generic_form_page.html'
    success_url_name = 'grant_applications:about-your-business'
    page = {
        'heading': _('Select your company')
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_choices'] = _get_company_select_choices(
            search_term=self.request.GET.get('search_term') or self.request.session['search_term']
        )
        return kwargs


class AboutYourBusinessView(PageContextMixin, SuccessUrlObjectPkMixin, UpdateView):
    model = GrantApplication
    fields = []
    template_name = 'grant_applications/about_your_business.html'
    success_url_name = 'grant_applications:about-you'
    page = {
        'heading': _('About your business')
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['company'] = DnbServiceClient().get_company(
                duns_number=self.object.duns_number
            )
        except DnbServiceClientException:
            context['company'] = {
                'primary_name': 'Could not retrieve company name.',
                'duns_number': self.object.duns_number,
            }
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
    template_name = 'grant_applications/generic_form_page.html'
    success_url_name = 'grant_applications:event-intention'
    page = {
        'heading': _('Your application')
    }


class EventIntentionView(PageContextMixin, SuccessUrlObjectPkMixin, UpdateView):
    model = GrantApplication
    form_class = EventIntentionForm
    template_name = 'grant_applications/generic_form_page.html'
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


class BusinessInformationView(PageContextMixin, SuccessUrlObjectPkMixin, UpdateView):
    model = GrantApplication
    form_class = BusinessInformationForm
    template_name = 'grant_applications/generic_form_page.html'
    success_url_name = 'grant_applications:state-aid'
    page = {
        'heading': _('About your business')
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
    fields = []
    template_name = 'grant_applications/application_review.html'
    page = {
        'heading': _('Review your application'),
        'form_button_text': _('Accept and send'),
    }

    def get_success_url(self):
        return reverse(
            'grant_applications:confirmation',
            kwargs={
                'pk': self.object.pk,
                'process_pk': self.process.pk,
            }
        )

    def _generate_summary_list(self):
        ga_form = model_forms.modelform_factory(GrantApplication, fields='__all__')
        summary_list = [
            {'key': v.label, 'value': getattr(self.object, k)}
            for k, v in ga_form.base_fields.items()
        ]
        summary_list[-1]['action'] = {
            'text': _('Change'),
            'url': reverse('grant_applications:about-your-business', args=(self.object.pk,)),
        }
        return summary_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['summary_list'] = self._generate_summary_list()
        return context

    def form_valid(self, form):
        self.process = GrantApplicationFlow.start.run(grant_application=self.object)
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
