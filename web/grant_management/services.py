from django.utils.translation import gettext_lazy as _
from web.companies.services import DnbServiceClient


class SupportingInformationContent:

    def __init__(self, grant_application):
        super().__init__()
        self.grant_application = grant_application
        self.dnb_client = DnbServiceClient()
        self._company = None

    @property
    def company(self):
        if self._company is None:
            self._company = self.dnb_client.get_company(self.grant_application.duns_number)
        return self._company

    @property
    def employee_count_content(self):
        e_or_r = 'reports'
        if self.company['is_employees_number_estimated']:
            e_or_r = 'estimates'

        return [
            _(f"The applicant indicated that the company has "
              f"{self.grant_application.number_of_employees} employees."),
            _(f"Dun & Bradstreet {e_or_r} that this company has {self.company['employee_number']}"
              f" employees."),
        ]

    @property
    def turnover_count_content(self):
        return [
            _(f"The applicant indicated that the company has a turnover of "
              f"£{self.grant_application.turnover}"),
        ]
