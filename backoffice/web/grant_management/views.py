from viewflow.flow.views import UpdateProcessView

from web.grant_management.mixins import SupportingInformationMixin


class BaseGrantManagementView(SupportingInformationMixin, UpdateProcessView):
    extra_context = {
        'information_card_title': 'Applicant response',
        'form_heading': 'Your assessment',
    }
