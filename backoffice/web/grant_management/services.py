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
    def verify_previous_applications_content(self):
        return {
            'tables': [
                {
                    'headers': [_('Eligibility criteria')],
                    'rows': [
                        [_('Businesses can have up to 6 TAP grants in total.')]
                    ]
                },
                {
                    'headers': [_('Application answers')],
                    'rows': [
                        [_(f"The applicant indicated that the business has has "
                           f"{self.grant_application.previous_applications} previous TAP grants.")]
                    ]
                }
            ]
        }

    @property
    def verify_event_commitment_content(self):
        has = 'has' if self.grant_application.is_already_committed_to_event else 'has not'
        return {
            'tables': [
                {
                    'headers': [_('Eligibility criteria')],
                    'rows': [
                        [_('Businesses cannot have committed to the event before applying for a '
                           'TAP grant.')]
                    ]
                },
                {
                    'headers': [_('Application answers')],
                    'rows': [
                        [_(f"The applicant indicated that the business {has} already committed to "
                           f"the event.")]
                    ]
                }
            ]
        }

    @property
    def verify_business_entity_content(self):
        content = {
            'tables': [
                {
                    'headers': [_('Eligibility criteria')],
                    'rows': [
                        [_('Businesses should have less that 250 employees.')],
                        [_('Annual Turnover should be between £83,000 and £5 million.')]
                    ]
                },
                {
                    'headers': [_('Application answers')],
                    'rows': [
                        [_(f"The applicant indicated that the company has "
                           f"{self.grant_application.number_of_employees} employees.")],
                        [_(f"The applicant indicated that the company has a turnover of "
                           f"£{self.grant_application.previous_years_turnover_1}.")]
                    ]
                },
                {
                    'headers': [_('Dun and Bradstreet')],
                    'rows': []
                }
            ]
        }

        if self.dnb_company_data:
            # Include Dun & Bradstreet data for number_of_employees
            e_or_r = 'reports'
            if self.dnb_company_data['is_employees_number_estimated']:
                e_or_r = 'estimates'
            content['tables'][2]['rows'].append([_(
                f"Dun & Bradstreet {e_or_r} that this company has "
                f"{self.dnb_company_data['employee_number']} employees."
            )])

            # Include Dun & Bradstreet data for annual_sales (turnover)
            content['tables'][2]['rows'].append([_(
                f"Dun & Bradstreet reports that this company has a turnover of "
                f"£{int(self.dnb_company_data['annual_sales'])}."
            )])
        else:
            content['tables'][2]['rows'].append([_(
                f"Could not retrieve Dun & Bradstreet data. {self.MSGS['contact-admin']}"
            )])

        return content

    @property
    def verify_state_aid_content(self):
        rows = [
            [s['authority'], s['amount'], s['description'], s['date_received']]
            for s in self.grant_application.stateaid_set.all()
        ]
        if not rows:
            rows = [['—', '—', '—', '—']]
        return {
            'tables': [
                {
                    'headers': ['Authority', 'Amount', 'Description', 'Date received'],
                    'rows': rows
                },
            ]
        }

    @property
    def decision_content(self):
        return {
            'links': [
                {
                    'url': 'https://www.gov.uk/guidance/tradeshow-access-programme#eligibility',
                }
            ]
        }
