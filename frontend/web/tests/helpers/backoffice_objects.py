FAKE_GRANT_APPLICATION = {
    'id': '993c394c-dd5d-413c-bd70-1ba4f1e2b050',
    'applicant_full_name': 'A',
    'applicant_email': 'A@test.com',
    'applicant_mobile_number': '+447777777777',
    'applicant_position_within_business': 'Director',
    'is_already_committed_to_event': True,
    'is_intending_on_other_financial_support': True,
    'has_previously_applied': True,
    'previous_applications': 1,
    'is_first_exhibit_at_event': False,
    'number_of_times_exhibited_at_event': 2,
    'goods_and_services_description': 'E',
    'business_name_at_exhibit': 'F',
    'other_business_names': 'G',
    'number_of_employees': 'fewer-than-10',
    'turnover': 1000,
    'website': 'www.test.com',
    'has_exported_before': False,
    'is_planning_to_grow_exports': True,
    'is_seeking_export_opportunities': True,
    'has_received_de_minimis_aid': False,
    'de_minimis_aid_public_authority': None,
    'de_minimis_aid_date_awarded': None,
    'de_minimis_aid_amount': None,
    'de_minimis_aid_description': None,
    'de_minimis_aid_recipient': None,
    'de_minimis_aid_date_received': None,
    'event': {
        'id': '235678a7-b3ff-4256-b6ae-ce7ddb4d18gg',
        'name': 'Event 1',
        'sector': 'Sector 1',
        'start_date': '2020-12-12',
        'end_date': '2020-12-14'
    },
    'company': {
        'id': '0dc205e4-1f11-4a81-90a6-f7a733da055e',
        'duns_number': '1234',
        'registration_number': '5678',
        'name': 'Company 1',
        'previous_applications': 1,
        'applications_in_review': 1,
        'last_dnb_get_company_response': {
            'id': '3cceee4e-32fa-4570-b8fa-514238823e25',
            'registration_number': '012345',
            'company_address': 'An address',
            'dnb_data': {
                'annual_sales': 1000,
                'employee_number': 3,
                'domain': 'www.test.com',
                'registration_numbers': []
            }
        }
    },
    'sector': {
        'id': 'e98cee83-9f4e-4ad2-8d10-7f25867b91b5',
        'name': 'Sector 1',
        'full_name': 'Sector 1',
    },
    'grant_management_process': {
        'id': '98d123ef-4218-4485-8285-c3c064f73893',
        'status': 'NEW',
        'grant_application': '993c394c-dd5d-413c-bd70-1ba4f1e2b050'
    }
}

FAKE_FLATTENED_GRANT_APPLICATION = FAKE_GRANT_APPLICATION.copy()
FAKE_FLATTENED_GRANT_APPLICATION['event'] = 'Event 1'
FAKE_FLATTENED_GRANT_APPLICATION['company'] = 'Company 1'
FAKE_FLATTENED_GRANT_APPLICATION['duns_number'] = 1
FAKE_FLATTENED_GRANT_APPLICATION['sector'] = 'Sector 1'
FAKE_FLATTENED_GRANT_APPLICATION['grant_management_process'] = \
    '98d123ef-4218-4485-8285-c3c064f73893'

FAKE_GRANT_MANAGEMENT_PROCESS = {
    'id': 'bcccc6df-d144-4cac-af39-3c693588ab20',
    'grant_application': '993c394c-dd5d-413c-bd70-1ba4f1e2b050',
    'employee_count_is_verified': None,
    'turnover_is_verified': None,
    'decision': None,
}

FAKE_COMPANY = {
    'id': '0dc205e4-1f11-4a81-90a6-f7a733da055e',
    'duns_number': '1234',
    'registration_number': '5678',
    'name': 'Company 1'
}

FAKE_SEARCH_COMPANIES = [{
    'id': '70c53a9c-eb5b-4547-9e26-967c719e1ba0',
    'company': None,
    'company_address': None,
    'registration_number': '5678',
    'dnb_data': {
        'primary_name': 'Company 1',
        'duns_number': '1234',
        'registration_numbers': [
            {'registration_number': '5678', 'registration_type': 'uk_companies_house_number'}
        ]
    }
}]


FAKE_EVENT = {
    'id': '235678a7-b3ff-4256-b6ae-ce7ddb4d18gg',
    'name': 'Event 1',
    'sector': 'Sector 1',
    'sub_sector': 'Sub Sector 1',
    'city': 'City 1',
    'country': 'Country 1',
    'start_date': '2020-12-12',
    'end_date': '2020-12-14',
    'display_name': 'Event 1 | Sector 1 | Country 1 | 2020-12-12',
    'tcp': 'TCP 1',
    'tcp_website': 'TCP Website 1',
}

FAKE_PAGINATED_LIST_EVENTS = {
  'count': 5,
  'next': 'https://host/api/trade-events/?page=4&page_size=1',
  'previous': 'https://host/api/trade-events/?page=2&page_size=1',
  'results': [FAKE_EVENT],
  'total_pages': 5
}

FAKE_SECTOR = {
    'id': 'e98cee83-9f4e-4ad2-8d10-7f25867b91b5',
    'sector_code': 'SL0001',
    'name': 'Sector 1',
    'cluster_name': 'Sector 1 Cluster',
    'full_name': 'Sector 1 Full Name',
    'sub_sector_name': 'Sector 1 Sub Sector Name',
    'sub_sub_sector_name': 'Sector 1 Sub Sub Sector Name'
}
