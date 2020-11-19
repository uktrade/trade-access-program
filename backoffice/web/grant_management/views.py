from viewflow.flow.views import UpdateProcessView

from web.grant_management.forms import (
    VerifyPreviousApplicationsForm, VerifyEventCommitmentForm,
    VerifyBusinessEntityForm, VerifyStateAidForm
)
from web.grant_management.mixins import SupportingInformationMixin


class VerifyPreviousApplicationsView(SupportingInformationMixin, UpdateProcessView):
    form_class = VerifyPreviousApplicationsForm


class VerifyEventCommitmentView(SupportingInformationMixin, UpdateProcessView):
    form_class = VerifyEventCommitmentForm


class VerifyBusinessEntityView(SupportingInformationMixin, UpdateProcessView):
    form_class = VerifyBusinessEntityForm


class VerifyStateAidView(SupportingInformationMixin, UpdateProcessView):
    form_class = VerifyStateAidForm


class DecisionView(SupportingInformationMixin, UpdateProcessView):
    fields = ['decision']
