FAKE_GRANT_APPLICATION = {
    'id': '993c394c-dd5d-413c-bd70-1ba4f1e2b050',
    'applicant_full_name': 'A',
    'applicant_email': 'A@test.com',
    'is_already_committed_to_event': True,
    'is_intending_on_other_financial_support': True,
    'has_previously_applied': True,
    'previous_applications': 1,
    'is_first_exhibit_at_event': False,
    'number_of_times_exhibited_at_event': 2,
    'goods_and_services_description': 'E',
    'business_name_at_exhibit': 'E',
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
        'id': 1,
        'name': 'Event 1',
        'sector': 'Sector 1',
        'start_date': '2020-12-12',
        'end_date': '2020-12-14'
    },
    'company': {
        'id': '0dc205e4-1f11-4a81-90a6-f7a733da055e',
        'duns_number': 1,
        'name': 'ABC',
        'previous_applications': 1,
        'applications_in_review': 1,
        'last_dnb_get_company_response': {
            'id': '3cceee4e-32fa-4570-b8fa-514238823e25',
            'company_registration_number': '012345',
            'company_address': 'An address',
            'data': {
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
FAKE_FLATTENED_GRANT_APPLICATION['company'] = 'ABC'
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
    'duns_number': 1234,
    'name': 'ABC'
}

FAKE_SEARCH_COMPANIES = [
    {'duns_number': '1', 'primary_name': 'Company 1'},
    {'duns_number': '2', 'primary_name': 'Company 2'}
]

FAKE_EVENT = {
    'id': 1,
    'display_name': 'An Event'
}

FAKE_SECTOR = {
    'id': 'ee211091-9b84-4460-a626-3be843823901',
    'sector_code': 'SL0001',
    'cluster_name': 'Technology and Advanced Manufacturing',
    'full_name': 'Advanced engineering',
    'name': 'Advanced engineering'
}
