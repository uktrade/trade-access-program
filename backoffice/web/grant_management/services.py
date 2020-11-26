from web.companies.services import DnbServiceClient, CompaniesHouseClient
from web.core.exceptions import DnbServiceClientException


class SupportingInformationContent:
    msgs = {
        'contact-admin': 'Please try again later or contact the site administrator.'
    }

    def __init__(self, grant_application):
        super().__init__()
        self.grant_application = grant_application
        self.dnb_client = DnbServiceClient()
        self.ch_client = CompaniesHouseClient()
        self._dnb_company_data = None

    def _make_table(self, headers=None, rows=None, col_tags=None):
        return {
            'headers': headers or [],
            'rows': rows or [],
            'col_tags': col_tags or []
        }

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
    def verify_business_entity_content(self):
        if self.dnb_company_data:
            return {
                'employee_number': self.dnb_company_data['employee_number'],
                'annual_sales': int(self.dnb_company_data['annual_sales'] or 0),
                'annual_sales_currency': self.dnb_company_data['annual_sales_currency']
            }

    @property
    def verify_state_aid_content(self):
        rows = [
            [s.authority, s.amount, s.description, s.date_received.strftime('%B %Y')]
            for s in self.grant_application.stateaid_set.all()
        ]
        return {
            'table': self._make_table(
                    headers=['Authority', 'Amount', 'Description', 'Date received'],
                    rows=rows or [['—', '—', '—', '—']]
                )
        }

    @property
    def decision_content(self):
        grant_management_process = self.grant_application.grant_management_process
        return {
            'table': self._make_table(
                rows=[
                    [
                        'Eligibility criteria',
                        f'{grant_management_process.total_verified}/4'
                    ],
                    [
                        'Suitability score',
                        f'{grant_management_process.suitability_score}/15'
                    ],
                    [
                        'Is the trade show appropriate?',
                        'Yes' if grant_management_process.event_is_appropriate else 'No'
                    ]
                ],
                col_tags=["style=width:75%", "style=width:25%"]
            )
        }
