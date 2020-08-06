from django.utils.translation import gettext_lazy as _
from viewflow.flow.views import UpdateProcessView

from web.grant_management.mixins import SupportingInformationMixin
from web.grant_management.services import SupportingInformation


class ApplicationAcknowledgementView(SupportingInformationMixin, UpdateProcessView):

    def get_supporting_information_card(self):
        return {
            'table': {
                'headers': [_('Question'), _('Answer')],
                'rows': self.activation.process.grant_application.application_summary,
            }
        }


class VerifyEmployeeCountView(SupportingInformationMixin, UpdateProcessView):
    fields = ['employee_count_is_verified']

    def get_supporting_information_card(self):
        return {
            'list': SupportingInformation.get_employee_count_content(self.object.grant_application)
        }
