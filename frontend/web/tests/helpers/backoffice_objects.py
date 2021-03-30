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

FAKE_COMPANY = {
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

FAKE_GRANT_APPLICATION = {
    'id': '993c394c-dd5d-413c-bd70-1ba4f1e2b050',
    'is_eligible': True,
    'previous_applications': 1,
    'event': FAKE_EVENT,
    'is_already_committed_to_event': True,
    'search_term': 'company-1',
    'company': FAKE_COMPANY,
    'manual_company_type': None,
    'manual_company_name': None,
    'manual_company_address_line_1': None,
    'manual_company_address_line_2': None,
    'manual_company_address_town': None,
    'manual_company_address_county': None,
    'manual_company_address_postcode': None,
    'manual_time_trading_in_uk': None,
    'manual_registration_number': None,
    'manual_vat_number': None,
    'manual_website': None,
    'number_of_employees': 'fewer-than-10',
    'is_turnover_greater_than': True,
    'applicant_full_name': 'A',
    'applicant_email': 'A@test.com',
    'applicant_mobile_number': '+447777777777',
    'job_title': 'Director',
    'previous_years_turnover_1': 1001,
    'previous_years_turnover_2': 1002,
    'previous_years_turnover_3': 1003,
    'previous_years_export_turnover_1': 101,
    'previous_years_export_turnover_2': 102,
    'previous_years_export_turnover_3': 103,
    'sector': FAKE_SECTOR,
    'other_business_names': 'D',
    'products_and_services_description': 'E',
    'products_and_services_competitors': 'F',
    'has_exported_before': False,
    'has_product_or_service_for_export': True,
    'has_exported_in_last_12_months': False,
    'export_regions': ['europe', 'asia pacific', 'africa'],
    'markets_intending_on_exporting_to': ['new', 'existing'],
    'is_in_contact_with_dit_trade_advisor': True,
    'ita_name': 'A Person',
    'ita_email': 'tcp@test.com',
    'ita_mobile_number': '07777777777',
    'export_experience_description': 'A description',
    'export_strategy': 'A strategy',
    'interest_in_event_description': 'A description',
    'is_in_contact_with_tcp': False,
    'tcp_name': 'A Name',
    'tcp_email': 'tcp@test.com',
    'tcp_mobile_number': '+447777777777',
    'is_intending_to_exhibit_as_tcp_stand': True,
    'stand_trade_name': 'A Name',
    'trade_show_experience_description': 'A description',
    'additional_guidance': 'Some additional guidance',
    'sent_for_review': False,
    'is_completed': False
}

FAKE_STATE_AID = {
    'id': '37a6898f-3c16-4fdf-8454-ff86c16c6454',
    'authority': 'An authority',
    'date_received': '2020-02-14',
    'amount': 2000,
    'description': 'A description',
}

FAKE_GRANT_MANAGEMENT_PROCESS = {
    'id': 'bcccc6df-d144-4cac-af39-3c693588ab20',
    'status': 'NEW',
    'finished': False,
    'decision': None,
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

FAKE_PAGINATED_LIST_EVENTS = {
  'count': 5,
  'next': 'https://host/api/trade-events/?page=4&page_size=1',
  'previous': 'https://host/api/trade-events/?page=2&page_size=1',
  'results': [FAKE_EVENT],
  'total_pages': 5
}

FAKE_TRADE_EVENT_AGGREGATES = {
    'total_trade_events': '4',
    'trade_event_months': [
        'December 2020',
        'February 2021'
    ],
}
