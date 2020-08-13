from django.utils.translation import gettext_lazy as _
from web.companies.services import DnbServiceClient
from web.core.exceptions import DnbServiceClientException


class SupportingInformationContent:

    def __init__(self, grant_application):
        super().__init__()
        self.grant_application = grant_application
        self.dnb_client = DnbServiceClient()
        self._dnb_company = None

    @property
    def dnb_company(self):
        if self._dnb_company is None and self.grant_application.company:
            try:
                self._dnb_company = self.dnb_client.get_company(
                    self.grant_application.company.dnb_service_duns_number
                )
            except DnbServiceClientException:
                pass
        return self._dnb_company

    @property
    def application_acknowledgement_content(self):
        return {
            'tables': [
                {
                    'class': 'striped',
                    'headers': [_('Question'), _('Answer')],
                    'rows': self.grant_application.answers
                }
            ]
        }

    @property
    def employee_count_content(self):
        content = {
            'tables': [
                {
                    'headers': [_('Evidence')],
                    'rows': [
                        [_(f"The applicant indicated that the company has "
                           f"{self.grant_application.number_of_employees} employees.")],
                    ]
                }
            ]
        }

        if self.dnb_company:
            e_or_r = 'reports'
            if self.dnb_company['is_employees_number_estimated']:
                e_or_r = 'estimates'
            content['tables'][0]['rows'].append([_(
                f"Dun & Bradstreet {e_or_r} that this company has "
                f"{self.dnb_company['employee_number']} employees."
            )])
        else:
            content['tables'][0]['rows'].append([_(
                "Could not retrieve Dun & Bradstreet data. "
                "Please try again later or contact the site administrator."
            )])

        return content

    @property
    def turnover_content(self):
        return {
            'tables': [
                {
                    'headers': [_('Eligibility')],
                    'rows': [
                        [_('Annual Turnover should be between £83,000 and £5 million.')]
                    ]
                },
                {
                    'headers': [_('Evidence')],
                    'rows': [
                        [_(f"The applicant indicated that the company has a turnover of "
                           f"£{self.grant_application.turnover}")],
                    ]
                }
            ]
        }

    @property
    def decision_content(self):
        return {
            'links': [
                {
                    'text': 'https://www.gov.uk/guidance/tradeshow-access-programme#eligibility',
                    'url': 'https://www.gov.uk/guidance/tradeshow-access-programme#eligibility',
                }
            ]
        }
