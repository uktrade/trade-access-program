from viewflow.flow.views import UpdateProcessView

from web.grant_management.forms import (
    VerifyPreviousApplicationsForm, VerifyEventCommitmentForm,
    VerifyBusinessEntityForm, VerifyStateAidForm
)
from web.grant_management.mixins import SupportingInformationMixin


class VerifyPreviousApplicationsView(SupportingInformationMixin, UpdateProcessView):
    form_class = VerifyPreviousApplicationsForm

    def get_supporting_information(self):
        return self.supporting_information.verify_previous_applications_content


class VerifyEventCommitmentView(SupportingInformationMixin, UpdateProcessView):
    form_class = VerifyEventCommitmentForm

    def get_supporting_information(self):
        return self.supporting_information.verify_event_commitment_content


class VerifyBusinessEntityView(SupportingInformationMixin, UpdateProcessView):
    form_class = VerifyBusinessEntityForm

    def get_supporting_information(self):
        return self.supporting_information.verify_business_entity_content


class VerifyStateAidView(SupportingInformationMixin, UpdateProcessView):
    form_class = VerifyStateAidForm

    def get_supporting_information(self):
        return self.supporting_information.verify_state_aid_content


class DecisionView(SupportingInformationMixin, UpdateProcessView):
    fields = ['decision']

    def get_supporting_information(self):
        return self.supporting_information.decision_content
