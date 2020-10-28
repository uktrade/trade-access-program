from decimal import Decimal
from unittest.mock import patch

from bs4 import BeautifulSoup
from django.urls import reverse

from web.grant_applications.forms import CompanyTradingDetailsForm
from web.grant_applications.services import BackofficeService
from web.grant_applications.views import CompanyTradingDetailsView
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import FAKE_GRANT_APPLICATION, FAKE_SECTOR
from web.tests.helpers.testcases import BaseTestCase


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'list_sectors', return_value=[FAKE_SECTOR])
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestCompanyTradingDetailsView(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.currency_fields = [
            'previous_years_turnover_1', 'previous_years_turnover_2', 'previous_years_turnover_3',
            'previous_years_export_turnover_1', 'previous_years_export_turnover_2',
            'previous_years_export_turnover_3',
        ]

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:company-trading-details', kwargs={'pk': self.gal.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, CompanyTradingDetailsView.template_name)

    def test_sector_choices_come_from_sector_list(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        options = soup.find_all('option')
        self.assertEqual(options[1].text, FAKE_SECTOR['full_name'])

    def test_post(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'previous_years_turnover_1': '1.23',
                'previous_years_turnover_2': '1.23',
                'previous_years_turnover_3': '1.23',
                'previous_years_export_turnover_1': '1.23',
                'previous_years_export_turnover_2': '1.23',
                'previous_years_export_turnover_3': '1.23',
                'sector': FAKE_SECTOR['id'],
                'other_business_names': 'A name',
                'products_and_services_description': 'A description',
                'products_and_services_competitors': 'A description'
            }
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            previous_years_turnover_1=Decimal('1.23'),
            previous_years_turnover_2=Decimal('1.23'),
            previous_years_turnover_3=Decimal('1.23'),
            previous_years_export_turnover_1=Decimal('1.23'),
            previous_years_export_turnover_2=Decimal('1.23'),
            previous_years_export_turnover_3=Decimal('1.23'),
            sector=FAKE_SECTOR['id'],
            other_business_names='A name',
            products_and_services_description='A description',
            products_and_services_competitors='A description'
        )

    def test_other_business_names_not_required(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'previous_years_turnover_1': '1.23',
                'previous_years_turnover_2': '1.23',
                'previous_years_turnover_3': '0',
                'previous_years_export_turnover_1': '1.23',
                'previous_years_export_turnover_2': '1.23',
                'previous_years_export_turnover_3': '0',
                'sector': FAKE_SECTOR['id'],
                'products_and_services_description': 'A description',
                'products_and_services_competitors': 'A description'
            }
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            previous_years_turnover_1=Decimal('1.23'),
            previous_years_turnover_2=Decimal('1.23'),
            previous_years_turnover_3=Decimal('0'),
            previous_years_export_turnover_1=Decimal('1.23'),
            previous_years_export_turnover_2=Decimal('1.23'),
            previous_years_export_turnover_3=Decimal('0'),
            sector=FAKE_SECTOR['id'],
            # We expect field to be explicitly set to None to overwrite any previously entered value
            other_business_names=None,
            products_and_services_description='A description',
            products_and_services_competitors='A description'
        )

    def test_initial_form_data_from_grant_application_object(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(
            soup.find(id='id_sector').find('option', selected=True).attrs['value'],
            FAKE_GRANT_APPLICATION['sector']['id']
        )
        for field in CompanyTradingDetailsForm.Meta.fields:
            if field == 'sector':
                continue
            html = soup.find(id=f'id_{field}')
            expected = html.attrs.get('value') or html.text
            self.assertEqual(expected, str(FAKE_GRANT_APPLICATION[field]))

    def test_validation_of_currency_fields_negative(self, *mocks):
        value = '-1'
        response = self.client.post(
            self.url,
            data={
                'sector': FAKE_SECTOR['id'],
                'products_and_services_description': 'A description',
                'products_and_services_competitors': 'A description',
                **{k: value for k in self.currency_fields}
            }
        )
        self.assertEqual(response.status_code, 200)
        for field in self.currency_fields:
            self.assertFormError(response, 'form', field, self.form_msgs['positive'])

    def test_validation_of_currency_fields_too_many_decimal_places(self, *mocks):
        value = '1.234'
        response = self.client.post(
            self.url,
            data={
                'sector': FAKE_SECTOR['id'],
                'products_and_services_description': 'A description',
                'products_and_services_competitors': 'A description',
                **{k: value for k in self.currency_fields}
            }
        )
        self.assertEqual(response.status_code, 200)
        for field in self.currency_fields:
            self.assertFormError(response, 'form', field, self.form_msgs['2dp'])

    def test_redirect_to_confirmation_page_if_application_already_sent_for_review(self, *mocks):
        self.gal.sent_for_review = True
        self.gal.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )
