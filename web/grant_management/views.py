from django.utils.translation import gettext_lazy as _
from viewflow.flow.views import UpdateProcessView

from web.grant_management.mixins import SupportingInformationMixin


class ApplicationAcknowledgementView(SupportingInformationMixin, UpdateProcessView):

    def get_supporting_information(self):
        return {
            'table': {
                'headers': [_('Question'), _('Answer')],
                'rows': self.activation.process.grant_application.application_summary,
            }
        }


class VerifyEmployeeCountView(SupportingInformationMixin, UpdateProcessView):
    fields = ['employee_count_is_verified']

    def get_supporting_information(self):
        return {
            'list': self.supporting_information.employee_count_content
        }


class VerifyTurnoverView(SupportingInformationMixin, UpdateProcessView):
    fields = ['turnover_is_verified']

    def get_supporting_information(self):
        return {
            'list': self.supporting_information.turnover_count_content
        }
