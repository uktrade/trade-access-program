from viewflow.flow.views import UpdateProcessView

from web.grant_management.mixins import SupportingInformationMixin


class ApplicationAcknowledgementView(SupportingInformationMixin, UpdateProcessView):

    def get_supporting_information(self):
        return self.supporting_information.application_acknowledgement_content


class VerifyEmployeeCountView(SupportingInformationMixin, UpdateProcessView):
    fields = ['employee_count_is_verified']

    def get_supporting_information(self):
        return self.supporting_information.employee_count_content


class VerifyTurnoverView(SupportingInformationMixin, UpdateProcessView):
    fields = ['turnover_is_verified']

    def get_supporting_information(self):
        return self.supporting_information.turnover_content


class DecisionView(SupportingInformationMixin, UpdateProcessView):
    fields = ['decision']

    def get_supporting_information(self):
        return self.supporting_information.decision_content
