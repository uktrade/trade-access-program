from unittest.mock import patch

from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from web.grant_applications.models import GrantApplication
from web.grant_management.models import GrantManagementProcess
from web.tests.factories.companies import CompanyFactory
from web.tests.factories.events import EventFactory
from web.tests.factories.grant_applications import GrantApplicationFactory
from web.tests.helpers import BaseAPITestCase


@patch('web.grant_management.flows.NotifyService')
class GrantApplicationsApiTests(BaseAPITestCase):

    def test_get_grant_application_detail(self, *mocks):
        ga = GrantApplicationFactory()
        path = reverse('grant-applications-detail', args=(ga.id,))
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(
            response,
            data_contains={
                'id': ga.id_str,
                'search_term': ga.search_term,
                'company': {
                    'id': ga.company.id_str,
                    'duns_number': ga.company.duns_number,
                    'name': ga.company.name,
                    'previous_applications': 0,
                    'applications_in_review': 0,
                },
                'applicant_full_name': ga.applicant_full_name,
                'applicant_email': ga.applicant_email,
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
                'is_intending_on_other_financial_support':
                    ga.is_intending_on_other_financial_support,
                'has_previously_applied': ga.has_previously_applied,
                'previous_applications': ga.previous_applications,
                'is_first_exhibit_at_event': ga.is_first_exhibit_at_event,
                'number_of_times_exhibited_at_event': ga.number_of_times_exhibited_at_event,
                'goods_and_services_description': ga.goods_and_services_description,
                'business_name_at_exhibit': ga.business_name_at_exhibit,
                'turnover': ga.turnover,
                'number_of_employees': ga.number_of_employees,
                'sector': {
                    'id': ga.sector.id_str,
                    'full_name': ga.sector.full_name,
                },
                'website': ga.website,
                'has_exported_before': ga.has_exported_before,
                'is_planning_to_grow_exports': ga.is_planning_to_grow_exports,
                'is_seeking_export_opportunities': ga.is_seeking_export_opportunities,
                'has_received_de_minimis_aid': ga.has_received_de_minimis_aid,
                'de_minimis_aid_public_authority': ga.de_minimis_aid_public_authority,
                'de_minimis_aid_date_awarded': str(ga.de_minimis_aid_date_awarded.date()),
                'de_minimis_aid_amount': ga.de_minimis_aid_amount,
                'de_minimis_aid_description': ga.de_minimis_aid_description,
                'de_minimis_aid_recipient': ga.de_minimis_aid_recipient,
                'de_minimis_aid_date_received': str(ga.de_minimis_aid_date_received.date()),
                'application_summary': ga.application_summary,
            }
        )

    def test_list_grant_applications(self, *mocks):
        gas = GrantApplicationFactory.create_batch(size=3)
        path = reverse('grant-applications-list')
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

    def test_create_new_grant_application(self, *mocks):
        path = reverse('grant-applications-list')
        response = self.client.post(path, {'search_term': 'company-1'})
        self.assertEqual(response.status_code, HTTP_201_CREATED, msg=response.data)
        self.assert_response_data_contains(response, data_contains={'search_term': 'company-1'})

    def test_on_create_all_optional_fields_are_none(self, *mocks):
        path = reverse('grant-applications-list')
        company = CompanyFactory()
        response = self.client.post(
            path, data={'company': company.id, 'search_term': 'company-1'}
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED, msg=response.data)
        self.assert_response_data_contains(
            response,
            data_contains={
                'search_term': 'company-1',
                'company': company.id,
                'applicant_full_name': None,
                'applicant_email': None,
                'event': None,
                'is_already_committed_to_event': None,
                'is_intending_on_other_financial_support': None,
                'has_previously_applied': None,
                'previous_applications': None,
                'is_first_exhibit_at_event': None,
                'number_of_times_exhibited_at_event': None,
                'goods_and_services_description': None,
                'business_name_at_exhibit': None,
                'turnover': None,
                'number_of_employees': None,
                'sector': None,
                'website': None,
                'has_exported_before': None,
                'is_planning_to_grow_exports': None,
                'is_seeking_export_opportunities': None,
                'has_received_de_minimis_aid': None,
                'de_minimis_aid_public_authority': None,
                'de_minimis_aid_date_awarded': None,
                'de_minimis_aid_amount': None,
                'de_minimis_aid_description': None,
                'de_minimis_aid_recipient': None,
                'de_minimis_aid_date_received': None,
                'application_summary': [],
            }
        )

    def test_update_grant_application(self, *mocks):
        event = EventFactory()
        ga = GrantApplicationFactory()
        path = reverse('grant-applications-detail', args=(ga.id,))
        response = self.client.patch(path, {'event': event.id})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(response, data_contains={'event': event.id})

    def test_create_new_grant_application_with_existing_company(self, *mocks):
        path = reverse('grant-applications-list')
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
        ga = GrantApplicationFactory()
        path = reverse('grant-applications-send-for-review', args=(ga.id,))
        response = self.client.post(path)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['grant_management_process']['grant_application'], ga.id)
        self.assertTrue(GrantManagementProcess.objects.filter(grant_application=ga).exists())