from django.utils.translation import gettext_lazy as _

from web.companies.services import DnbServiceClient, CompaniesHouseClient
from web.core.exceptions import DnbServiceClientException


class SupportingInformationContent:
    msgs = {
        'contact-admin': 'Please try again later or contact the site administrator.'
    }
    headers = {
        'eligibility': _('Eligibility criteria'),
        'suitability': _('Suitability score'),
        'application': _('Application answers'),
        'dnb': _('Dun and Bradstreet'),
    }

    def __init__(self, grant_application):
        super().__init__()
        self.grant_application = grant_application
        self.dnb_client = DnbServiceClient()
        self.ch_client = CompaniesHouseClient()
        self._dnb_company_data = None

    def _table(self, headers, rows, col_tags=None):
        return {
            'headers': headers,
            'rows': rows,
            'col_tags': col_tags or []
        }

    def _make_paragraph(self, header, text):
        return {'header': header, 'text': text}

    def _make_link(self, header, url, text=None):
        return {'header': header, 'url': url, 'text': text}

    def _make_table(self, section, rows, col_tags=None):
        return self._table(
            headers=[self.headers[section]],
            rows=rows,
            col_tags=col_tags
        )

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
    def verify_previous_applications_content(self):
        return {
            'tables': [
                self._make_table(
                    section='eligibility',
                    rows=[[_('Businesses can have up to 6 TAP grants in total.')]]
                ),
                self._make_table(
                    section='application',
                    rows=[
                        [_(f"The applicant indicated that the business has has "
                           f"{self.grant_application.previous_applications} previous TAP grants.")]
                    ]
                ),
            ]
        }

    @property
    def verify_event_commitment_content(self):
        has = 'has' if self.grant_application.is_already_committed_to_event else 'has not'
        return {
            'tables': [
                self._make_table(
                    section='eligibility',
                    rows=[
                        [_('Businesses cannot have committed to the event before applying for a '
                            'TAP grant.')]
                    ]
                ),
                self._make_table(
                    section='application',
                    rows=[
                        [_(f"The applicant indicated that the business {has} already committed to "
                           f"the event.")]
                    ]
                )
            ]
        }

    @property
    def verify_business_entity_content(self):
        content = {
            'tables': [
                self._make_table(
                    section='eligibility',
                    rows=[
                        [_('Businesses should have less that 250 employees.')],
                        [_('Annual Turnover should be between £83,000 and £5 million.')]
                    ]
                ),
                self._make_table(
                    section='application',
                    rows=[
                        [_(f"The applicant indicated that the company has "
                           f"{self.grant_application.number_of_employees} employees.")],
                        [_(f"The applicant indicated that the company has a turnover of "
                           f"£{self.grant_application.previous_years_turnover_1}.")]
                    ]
                )
            ]
        }

        dnb_rows = [[_(f"Could not retrieve Dun & Bradstreet data. {self.msgs['contact-admin']}")]]
        if self.dnb_company_data:
            e_or_r = 'reports'
            if self.dnb_company_data['is_employees_number_estimated']:
                e_or_r = 'estimates'
            dnb_rows = [
                [_(  # Include Dun & Bradstreet data for number_of_employees
                    f"Dun & Bradstreet {e_or_r} that this company has "
                    f"{self.dnb_company_data['employee_number']} employees.")],
                [_(  # Include Dun & Bradstreet data for annual_sales (turnover)
                    f"Dun & Bradstreet reports that this company has a turnover of "
                    f"£{int(self.dnb_company_data['annual_sales'] or 0)}."
                )]
            ]

        content['tables'].append(
            self._make_table(section='dnb', rows=dnb_rows)
        )

        return content

    @property
    def verify_state_aid_content(self):
        rows = [
            [s.authority, s.amount, s.description, s.date_received]
            for s in self.grant_application.stateaid_set.all()
        ]
        if not rows:
            rows = [['—', '—', '—', '—']]
        return {
            'tables': [
                self._table(
                    headers=['Authority', 'Amount', 'Description', 'Date received'],
                    rows=rows
                )
            ]
        }

    @property
    def products_and_services_content(self):
        return {
            'tables': [
                self._make_table(
                    section='application',
                    rows=[[
                        'Describe your main products and services',
                        self.grant_application.products_and_services_description
                    ]],
                    col_tags=["style=width:50%", "style=width:50%"]
                ),
            ]
        }

    @property
    def products_and_services_competitors_content(self):
        return {
            'tables': [
                self._make_table(
                    section='application',
                    rows=[[
                        'Describe any advantages your products and services offer over competitors '
                        'in overseas markets',
                        self.grant_application.products_and_services_competitors
                    ]],
                    col_tags=["style=width:50%", "style=width:50%"]
                ),
            ]
        }

    @property
    def export_strategy_content(self):
        return {
            'tables': [
                self._make_table(
                    section='application',
                    rows=[[
                        'Provide a brief summary of your export strategy',
                        self.grant_application.export_strategy
                    ]],
                    col_tags=["style=width:50%", "style=width:50%"]
                ),
            ]
        }

    @property
    def event_is_appropriate_content(self):
        event = self.grant_application.event
        return {
            'paragraphs': [
                self._make_paragraph(
                    header='Event <i class="small material-icons">event</i>',
                    text=f'{event.name}\n'
                         f'{event.sub_sector}, {event.sector}\n'
                         f'{event.city}, {event.country}\n'
                         f'{event.start_date} to {event.start_date}\n'
                )
            ],
            'tables': [
                self._make_table(
                    section='application',
                    rows=[[
                        f'Why are you particularly interested in {event.name}',
                        self.grant_application.interest_in_event_description
                    ]],
                    col_tags=["style=width:50%", "style=width:50%"]
                ),
            ],
        }

    @property
    def decision_content(self):
        grant_management_process = self.grant_application.grant_management_process
        return {
            'tables': [
                self._table(
                    headers=['Application Review'],
                    rows=[
                        [
                            self.headers['eligibility'],
                            f'{grant_management_process.total_verified}/4'
                        ],
                        [
                            self.headers['suitability'],
                            f'{grant_management_process.suitability_score}/15'
                        ],
                        [
                            'Is the trade show appropriate?',
                            'Yes' if grant_management_process.event_is_appropriate else 'No'
                        ]
                    ],
                    col_tags=["style=width:75%", "style=width:25%"]
                ),
            ]
        }
