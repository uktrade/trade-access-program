from django.db import transaction
from django.urls import reverse
from django.utils.http import urlencode
from django.views.generic import FormView
from django.views.generic.base import TemplateView

from web.core.view_mixins import PageContextMixin
from web.grant_management.flows import GrantApplicationFlow
from web.grant_applications.forms import SubmitApplicationForm, SearchCompanyForm, SelectCompanyForm
from web.companies.models import Company
from web.companies.services import DnbServiceClient
from web.core.exceptions import DnbServiceClientException

from django.utils.translation import gettext_lazy as _


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
        'page_heading': _('Search for your company')
    }

    def get_success_url(self):
        return reverse('grant_applications:select-company') + f'?{urlencode(self.extra_context)}'

    def form_valid(self, form):
        self.extra_context = {'search_term': form.cleaned_data['search_term']}
        return super().form_valid(form)


class SelectCompanyView(PageContextMixin, FormView):
    form_class = SelectCompanyForm
    template_name = 'grant_applications/generic_form_page.html'
    page = {
        'page_heading': _('Select your company')
    }

    def get_success_url(self):
        return reverse('grant_applications:submit-application') + f'?{urlencode(self.kwargs)}'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if self.request.method == 'GET':
            self.request.session['search_term'] = self.request.GET['search_term']

        kwargs['company_choices'] = _get_company_select_choices(
            search_term=self.request.session['search_term']
        )

        return kwargs

    def form_valid(self, form):
        duns_number = form.cleaned_data['duns_number']
        Company.objects.get_or_create(dnb_service_duns_number=duns_number)
        self.kwargs['duns_number'] = duns_number
        return super().form_valid(form)


class SubmitApplicationView(PageContextMixin, FormView):
    form_class = SubmitApplicationForm
    template_name = 'grant_applications/submit_application.html'
    page = {
        'page_heading': _('Application Form')
    }

    def get_success_url(self):
        return reverse('grant_applications:confirmation', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['company'] = DnbServiceClient().get_company(
                duns_number=self.request.GET['duns_number']
            )
        except DnbServiceClientException:
            context['company'] = {
                'primary_name': 'Could not retrieve company name.',
                'duns_number': self.request.GET['duns_number'],
            }
        return context

    def form_valid(self, form):
        with transaction.atomic():
            process = GrantApplicationFlow.start.run(fields=form.cleaned_data)
            self.kwargs['process_pk'] = process.pk
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
