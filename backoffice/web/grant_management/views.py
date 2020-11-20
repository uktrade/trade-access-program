from viewflow.flow.views import UpdateProcessView

from web.grant_management.forms import (
    VerifyPreviousApplicationsForm, VerifyEventCommitmentForm,
    VerifyBusinessEntityForm, VerifyStateAidForm, ProductsAndServicesForm
)
from web.grant_management.mixins import SupportingInformationMixin


class VerifyPreviousApplicationsView(SupportingInformationMixin, UpdateProcessView):
    form_class = VerifyPreviousApplicationsForm
    extra_context = {
        'form_heading': 'Eligible'
    }


class VerifyEventCommitmentView(SupportingInformationMixin, UpdateProcessView):
    form_class = VerifyEventCommitmentForm
    extra_context = {
        'form_heading': 'Eligible'
    }


class VerifyBusinessEntityView(SupportingInformationMixin, UpdateProcessView):
    form_class = VerifyBusinessEntityForm
    extra_context = {
        'form_heading': 'Eligible'
    }


class VerifyStateAidView(SupportingInformationMixin, UpdateProcessView):
    form_class = VerifyStateAidForm
    extra_context = {
        'form_heading': 'Eligible'
    }


class DecisionView(SupportingInformationMixin, UpdateProcessView):
    fields = ['decision']


class ProductsAndServicesView(SupportingInformationMixin, UpdateProcessView):
    form_class = ProductsAndServicesForm
    extra_context = {
        'form_heading': "Please score the applicant's response"
    }
