from django.utils.translation import gettext_lazy as _

from web.companies.services import DnbServiceClient, CompaniesHouseClient
from web.core.exceptions import DnbServiceClientException


class SupportingInformationContent:
    MSGS = {
        'contact-admin': 'Please try again later or contact the site administrator.'
    }

    def __init__(self, grant_application):
        super().__init__()
        self.grant_application = grant_application
        self.dnb_client = DnbServiceClient()
        self.ch_client = CompaniesHouseClient()
        self._dnb_company_data = None

    @property
    def dnb_company_data(self):
        if self._dnb_company_data is None:
            # Look in local DB Cache first.
            dnb_company_response = self.grant_application.company.last_dnb_get_company_response
            if dnb_company_response:
                self._dnb_company_data = dnb_company_response.dnb_data

            # If not available then go to dnb-service
            if not self._dnb_company_data:
                try:
                    self._dnb_company_data = self.dnb_client.get_company(
                        duns_number=self.grant_application.company.duns_number
                    )
                except DnbServiceClientException:
                    # leave self._dnb_company as None if not available
                    pass
        return self._dnb_company_data

    @property
    def application_acknowledgement_content(self):
        tables = []

        for section in self.grant_application.application_summary:
            tables.append({
                'col_tags': ["style=width:50%", "style=width:50%"],
                'headers': [section['heading'], ''],
                'rows': [[row['key'], row['value']] for row in section['rows']]
            })

        return {'tables': tables}

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

        if self.dnb_company_data:
            e_or_r = 'reports'
            if self.dnb_company_data['is_employees_number_estimated']:
                e_or_r = 'estimates'
            content['tables'][0]['rows'].append([_(
                f"Dun & Bradstreet {e_or_r} that this company has "
                f"{self.dnb_company_data['employee_number']} employees."
            )])
        else:
            content['tables'][0]['rows'].append([_(
                f"Could not retrieve Dun & Bradstreet data. {self.MSGS['contact-admin']}"
            )])

        return content

    @property
    def turnover_content(self):
        content = {
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
                           f"£{self.grant_application.previous_years_turnover_1}.")]
                    ]
                }
            ]
        }

        if self.dnb_company_data:
            content['tables'][1]['rows'].append([_(
                f"Dun & Bradstreet reports that this company has a turnover of "
                f"£{int(self.dnb_company_data['annual_sales'])}."
            )])
        else:
            content['tables'][1]['rows'].append([_(
                f"Could not retrieve Dun & Bradstreet data. {self.MSGS['contact-admin']}"
            )])

        return content

    @property
    def decision_content(self):
        return {
            'links': [
                {
                    'url': 'https://www.gov.uk/guidance/tradeshow-access-programme#eligibility',
                }
            ]
        }
