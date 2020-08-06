from web.companies.services import DnbServiceClient


class SupportingInformation:

    @staticmethod
    def get_employee_count_content(grant_application):
        c = DnbServiceClient().get_company(grant_application.duns_number)

        e_or_r = 'reports'
        if c['is_employees_number_estimated']:
            e_or_r = 'estimates'

        return [
            f"The applicant indicated that the company has {grant_application.number_of_employees} "
            f"employees.",
            f"Dun & Bradstreet {e_or_r} that this company has {c['employee_number']} employees.",
        ]
