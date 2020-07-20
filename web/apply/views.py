from django.urls import reverse
from django.utils.http import urlencode
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from viewflow.flow.views import StartFlowMixin

from web.apply.forms import SubmitApplicationForm, SearchCompanyForm, SelectCompanyForm
from web.companies.models import Company
from web.companies.services import DnbServiceClient
from web.core.exceptions import DnbServiceClientException
from web.core.mixins import FlowFormSubmitMixin


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


class SearchCompanyView(FormView):
    form_class = SearchCompanyForm
    template_name = 'apply/search_company.html'

    def get_success_url(self):
        return reverse('apply:select-company') + f'?{urlencode(self.extra_context)}'

    def form_valid(self, form):
        self.extra_context = {'search_term': form.cleaned_data['search_term']}
        return super().form_valid(form)


class SelectCompanyView(FormView):
    form_class = SelectCompanyForm
    template_name = 'apply/select_company.html'

    def get_success_url(self):
        return reverse('viewflow:apply:apply:submit') + f'?{urlencode(self.extra_context)}'

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
        self.extra_context = {'duns_number': duns_number}
        return super().form_valid(form)


class SubmitApplicationView(FlowFormSubmitMixin, StartFlowMixin, FormView):
    form_class = SubmitApplicationForm

    def get_success_url(self):
        """Send user outside of viewflow urls confirmation page."""
        if '_continue' in self.request.POST and self.activation.process.pk:
            return reverse('apply:confirmation', args=(self.activation.process.pk,))
        return super().get_success_url()

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


class ConfirmationView(TemplateView):
    template_name = 'apply/confirmation.html'
