from web.companies.services import DnbServiceClient


def get_dnb_company_employee_count_content(duns_number):
    company = DnbServiceClient().get_company(duns_number)

    e_or_r = 'reports'
    if company['is_employees_number_estimated']:
        e_or_r = 'estimates'

    return f"Dun and Bradstreet {e_or_r} that this company has {company['employee_number']} " \
           f"employees."
