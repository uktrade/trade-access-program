from django.views.generic import FormView

from api.apply.forms import StartApplicationForm, EligibilityForm
from api.companies.services import DnbServiceClient


class StartApplicationView(FormView):
    template_name = 'start.html'
    form_class = StartApplicationForm
    success_url = '/apply/confirmation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = DnbServiceClient()
        dnb_company = client.get_company(duns_number=self.request.GET['company'])
        context['company'] = dnb_company
        return context


class EligibilityView(FormView):
    template_name = 'eligibility.html'
    form_class = EligibilityForm
    success_url = '/apply/eligibility'
