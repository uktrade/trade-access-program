from viewflow.flow.views import UpdateProcessView

from web.grant_management.mixins import SupportingInformationMixin


class BaseUpdateProcessView(SupportingInformationMixin, UpdateProcessView):
    pass


class BaseVerifyView(SupportingInformationMixin, UpdateProcessView):
    extra_context = {
        'form_heading': 'Eligible'
    }


class BaseScoreView(SupportingInformationMixin, UpdateProcessView):
    extra_context = {
        'form_heading': "Please score the applicant's response"
    }
