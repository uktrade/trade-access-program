from django.utils.translation import gettext_lazy as _
from viewflow.flow.views import UpdateProcessView

from web.grant_management.services import get_dnb_company_employee_count_content


class ApplicationAcknowledgementView(UpdateProcessView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_card'] = {
            'table': {
                'headers': [_('Question'), _('Answer')],
                'rows': self.activation.process.grant_application.application_summary,
            }
        }
        return context


class VerifyEmployeeCountView(UpdateProcessView):
    fields = ['employee_count_is_verified']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_card'] = {
            'list': [
                get_dnb_company_employee_count_content(self.object.grant_application.duns_number)
            ]
        }
        return context
