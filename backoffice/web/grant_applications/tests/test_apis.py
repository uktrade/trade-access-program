from unittest.mock import patch

from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST
)

from web.grant_applications.models import GrantApplication, StateAid
from web.grant_management.models import GrantManagementProcess
from web.tests.factories.companies import CompanyFactory
from web.tests.factories.events import EventFactory
from web.tests.factories.grant_applications import GrantApplicationFactory
from web.tests.factories.grant_management import GrantManagementProcessFactory
from web.tests.factories.state_aid import StateAidFactory
from web.tests.helpers import BaseAPITestCase


@patch('web.grant_applications.serializers.refresh_dnb_company_response_data')
@patch('web.grant_management.flows.NotifyService')
class GrantApplicationsApiTests(BaseAPITestCase):

    def test_get_grant_application_detail(self, *mocks):
        ga = GrantApplicationFactory()
        path = reverse('grant-applications:grant-applications-detail', args=(ga.id,))
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(
            response,
            data_contains={
                'id': ga.id_str,
                'previous_applications': ga.previous_applications,
                'event': {
                    'id': ga.event.id_str,
                    'city': ga.event.city,
                    'country': ga.event.country,
                    'name': ga.event.name,
                    'show_type': ga.event.show_type,
                    'start_date': str(ga.event.start_date),
                    'end_date': str(ga.event.end_date),
                    'sector': ga.event.sector,
                    'sub_sector': ga.event.sub_sector,
                    'tcp': ga.event.tcp,
                    'tcp_website': ga.event.tcp_website,
                },
                'is_already_committed_to_event': ga.is_already_committed_to_event,
                'search_term': ga.search_term,
                'company': {
                    'id': ga.company.id_str,
                    'duns_number': ga.company.duns_number,
                    'registration_number': ga.company.registration_number,
                    'name': ga.company.name,
                    'last_dnb_get_company_response': {
                        'id': ga.company.last_dnb_get_company_response.id_str,
                        'dnb_data': ga.company.last_dnb_get_company_response.dnb_data,
                        'company_address': ga.company.last_dnb_get_company_response.company_address,
                        'registration_number':
                            ga.company.last_dnb_get_company_response.registration_number
                    },
                    'previous_applications': 0,
                    'applications_in_review': 0,
                },
                'manual_company_type': ga.manual_company_type,
                'manual_company_name': ga.manual_company_name,
                'manual_company_address_line_1': ga.manual_company_address_line_1,
                'manual_company_address_line_2': ga.manual_company_address_line_2,
                'manual_company_address_town': ga.manual_company_address_town,
                'manual_company_address_county': ga.manual_company_address_county,
                'manual_company_address_postcode': ga.manual_company_address_postcode,
                'manual_time_trading_in_uk': ga.manual_time_trading_in_uk,
                'manual_registration_number': ga.manual_registration_number,
                'manual_vat_number': ga.manual_vat_number,
                'manual_website': ga.manual_website,
                'number_of_employees': ga.number_of_employees,
                'is_turnover_greater_than': ga.is_turnover_greater_than,
                'applicant_full_name': ga.applicant_full_name,
                'applicant_email': ga.applicant_email,
                'applicant_mobile_number': ga.applicant_mobile_number,
                'job_title': ga.job_title,
                'previous_years_turnover_1': str(ga.previous_years_turnover_1),
                'previous_years_turnover_2': str(ga.previous_years_turnover_2),
                'previous_years_turnover_3': str(ga.previous_years_turnover_3),
                'previous_years_export_turnover_1': str(ga.previous_years_export_turnover_1),
                'previous_years_export_turnover_2': str(ga.previous_years_export_turnover_2),
                'previous_years_export_turnover_3': str(ga.previous_years_export_turnover_3),
                'sector': {
                    'id': ga.sector.id_str,
                    'full_name': ga.sector.full_name,
                },
                'other_business_names': ga.other_business_names,
                'products_and_services_description': ga.products_and_services_description,
                'products_and_services_competitors': ga.products_and_services_competitors,
                'has_exported_before': ga.has_exported_before,
                'has_product_or_service_for_export': ga.has_product_or_service_for_export,
                'has_exported_in_last_12_months': ga.has_exported_in_last_12_months,
                'export_regions': ga.export_regions,
                'markets_intending_on_exporting_to': ga.markets_intending_on_exporting_to,
                'is_in_contact_with_dit_trade_advisor': ga.is_in_contact_with_dit_trade_advisor,
                'export_experience_description': ga.export_experience_description,
                'export_strategy': ga.export_strategy,
                'interest_in_event_description': ga.interest_in_event_description,
                'is_in_contact_with_tcp': ga.is_in_contact_with_tcp,
                'tcp_name': ga.tcp_name,
                'tcp_email': ga.tcp_email,
                'tcp_mobile_number': ga.tcp_mobile_number,
                'is_intending_to_exhibit_as_tcp_stand': ga.is_intending_to_exhibit_as_tcp_stand,
                'stand_trade_name': ga.stand_trade_name,
                'trade_show_experience_description': ga.trade_show_experience_description,
                'additional_guidance': ga.additional_guidance,
                'application_summary': ga.application_summary,
            }
        )

    def test_list_grant_applications(self, *mocks):
        gas = GrantApplicationFactory.create_batch(size=3)
        path = reverse('grant-applications:grant-applications-list')
        response = self.client.get(path=path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(
            response,
            data_contains=[
                {'id': gas[0].id_str},
                {'id': gas[1].id_str},
                {'id': gas[2].id_str}
            ]
        )

    def test_grant_application_counts(self, *mocks):
        company = CompanyFactory()

        # Create 2 approved grant applications for this company
        GrantManagementProcessFactory.create_batch(
            size=2,
            grant_application__company=company,
            decision=GrantManagementProcess.Decision.APPROVED
        )
        # Create 1 rejected grant application for this company
        GrantManagementProcessFactory(
            grant_application__company=company,
            decision=GrantManagementProcess.Decision.REJECTED
        )
        # Create a grant application which is currently under review
        GrantManagementProcessFactory(grant_application__company=company)

        # Create a new grant application
        ga = GrantApplicationFactory(company=company)
        path = reverse('grant-applications:grant-applications-detail', args=(ga.id,))

        response = self.client.get(path)
        self.assertEqual(response.data['company']['previous_applications'], 2)
        self.assertEqual(response.data['company']['applications_in_review'], 1)

    def test_create_new_grant_application(self, *mocks):
        path = reverse('grant-applications:grant-applications-list')
        response = self.client.post(path, {'search_term': 'company-1'})
        self.assertEqual(response.status_code, HTTP_201_CREATED, msg=response.data)
        self.assert_response_data_contains(response, data_contains={'search_term': 'company-1'})

    def test_on_create_all_fields_are_optional(self, *mocks):
        path = reverse('grant-applications:grant-applications-list')
        response = self.client.post(path)
        self.assertEqual(response.status_code, HTTP_201_CREATED, msg=response.data)

    def test_new_grant_application_refreshes_dnb_company_data(self, *mocks):
        path = reverse('grant-applications:grant-applications-list')
        company = CompanyFactory()
        self.client.post(path, data={'company': company.id, 'search_term': 'company-1'})
        mocks[1].assert_called_once_with(company)

    def test_new_grant_application_does_not_refresh_dnb_company_data_if_no_company(self, *mocks):
        path = reverse('grant-applications:grant-applications-list')
        self.client.post(path, data={'search_term': 'company-1'})
        mocks[1].assert_not_called()

    def test_update_grant_application(self, *mocks):
        event = EventFactory()
        ga = GrantApplicationFactory()
        path = reverse('grant-applications:grant-applications-detail', args=(ga.id,))
        response = self.client.patch(path, {'event': event.id})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(response, data_contains={'event': event.id})

    def test_create_new_grant_application_with_existing_company(self, *mocks):
        path = reverse('grant-applications:grant-applications-list')
        company = CompanyFactory()
        response = self.client.post(
            path,
            data={
                'search_term': 'company-1',
                'company': company.id_str
            }
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED, msg=response.data)
        self.assert_response_data_contains(response, data_contains={'search_term': 'company-1'})
        self.assertTrue(GrantApplication.objects.filter(company=company).exists())

    def test_grant_application_send_for_review(self, *mocks):
        ga = GrantApplicationFactory(application_summary=[])
        path = reverse('grant-applications:grant-applications-send-for-review', args=(ga.id,))
        response = self.client.post(path, data={'application_summary': 'A summary'})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['grant_management_process']['grant_application'], ga.id)
        self.assertTrue(GrantManagementProcess.objects.filter(grant_application=ga).exists())
        self.assertEqual(response.data['application_summary'], 'A summary')

    def test_grant_application_send_for_review_requires_application_summary(self, *mocks):
        ga = GrantApplicationFactory()
        path = reverse('grant-applications:grant-applications-send-for-review', args=(ga.id,))
        response = self.client.post(path)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['application_summary'][0].code, 'required')


class StateAidApiTests(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.ga = GrantApplicationFactory()

    def test_get_grant_application_detail(self, *mocks):
        state_aid = StateAidFactory(grant_application=self.ga)
        path = reverse('grant-applications:state-aid-detail', args=(state_aid.id,))
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(
            response,
            data_contains={
                'id': state_aid.id_str,
                'authority': state_aid.authority,
                'date_received': str(state_aid.date_received),
                'amount': state_aid.amount,
                'description': state_aid.description,
                'grant_application': self.ga.id
            }
        )

    def test_create_state_aid(self):
        path = reverse('grant-applications:state-aid-list')
        response = self.client.post(
            path,
            data={
                'authority': 'authority 1',
                'date_received': '2020-10-01',
                'amount': 1000,
                'description': 'A description',
                'grant_application': self.ga.id_str
            }
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED, msg=response.data)
        self.assertTrue(StateAid.objects.filter(grant_application=self.ga).exists())

    def test_delete_state_aid(self):
        state_aid = StateAidFactory(grant_application=self.ga)
        self.assertTrue(StateAid.objects.filter(grant_application=self.ga).exists())

        path = reverse('grant-applications:state-aid-detail', args=(state_aid.id,))
        response = self.client.delete(path)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT, msg=response.data)
        self.assertFalse(StateAid.objects.filter(grant_application=self.ga).exists())
