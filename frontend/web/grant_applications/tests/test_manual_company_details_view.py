from unittest.mock import patch

from django.urls import reverse

from web.grant_applications.forms import ManualCompanyDetailsForm
from web.grant_applications.services import BackofficeService
from web.grant_applications.views import ManualCompanyDetailsView
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import FAKE_GRANT_APPLICATION, FAKE_COMPANY
from web.tests.helpers.testcases import BaseTestCase


@patch.object(BackofficeService, 'create_company', return_value=FAKE_COMPANY)
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestManualCompanyDetailsView(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:manual-company-details', args=(self.gal.pk,))

    def test_get_template(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ManualCompanyDetailsView.template_name)

    def test_post(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'manual_company_type': ManualCompanyDetailsForm.CompanyType.LIMITED_COMPANY,
                'manual_company_name': 'A Name',
                'manual_company_address_line_1': 'Line 1',
                'manual_company_address_line_2': 'Line 2',
                'manual_company_address_town': 'Town 1',
                'manual_company_address_county': 'County 1',
                'manual_company_address_postcode': 'ZZ1 8ZZ',
                'manual_time_trading_in_uk':
                    ManualCompanyDetailsForm.TimeTradingInUk.TWO_TO_FIVE_YEARS,
                'manual_registration_number': '10000000',
                'manual_vat_number': '123456789',
                'manual_website': 'https://www.test.com'
            }
        )
        self.assertRedirects(
            response=response,
            expected_url=reverse('grant-applications:company-details', args=(self.gal.pk,))
        )
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            manual_company_type=ManualCompanyDetailsForm.CompanyType.LIMITED_COMPANY.value,
            manual_company_name='A Name',
            manual_company_address_line_1='Line 1',
            manual_company_address_line_2='Line 2',
            manual_company_address_town='Town 1',
            manual_company_address_county='County 1',
            manual_company_address_postcode='ZZ1 8ZZ',
            manual_time_trading_in_uk=ManualCompanyDetailsForm.TimeTradingInUk.TWO_TO_FIVE_YEARS,
            manual_registration_number='10000000',
            manual_vat_number='123456789',
            manual_website='https://www.test.com',
            company=None
        )

    def test_get_redirects_to_confirmation_if_application_already_sent_for_review(self, *mocks):
        self.gal.sent_for_review = True
        self.gal.save()
        response = self.client.get(self.url)
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )

    def test_required_fields(self, *mocks):
        response = self.client.post(self.url)
        msg = self.form_msgs['required']
        self.assertFormError(response, 'form', 'manual_company_type', msg)
        self.assertFormError(response, 'form', 'manual_company_name', msg)
        self.assertFormError(response, 'form', 'manual_company_address_line_1', msg)
        self.assertFormError(response, 'form', 'manual_company_address_line_2', msg)
        self.assertFormError(response, 'form', 'manual_company_address_town', msg)
        self.assertFormError(response, 'form', 'manual_company_address_county', msg)
        self.assertFormError(response, 'form', 'manual_company_address_postcode', msg)
        self.assertFormError(response, 'form', 'manual_time_trading_in_uk', msg)

    def test_optional_fields(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'manual_company_type': ManualCompanyDetailsForm.CompanyType.LIMITED_COMPANY,
                'manual_company_name': 'A Name',
                'manual_company_address_line_1': 'Line 1',
                'manual_company_address_line_2': 'Line 2',
                'manual_company_address_town': 'Town 1',
                'manual_company_address_county': 'County 1',
                'manual_company_address_postcode': 'ZZ1 8ZZ',
                'manual_time_trading_in_uk':
                    ManualCompanyDetailsForm.TimeTradingInUk.TWO_TO_FIVE_YEARS,
            }
        )
        self.assertRedirects(
            response=response,
            expected_url=reverse('grant-applications:company-details', args=(self.gal.pk,))
        )
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            manual_company_type=ManualCompanyDetailsForm.CompanyType.LIMITED_COMPANY.value,
            manual_company_name='A Name',
            manual_company_address_line_1='Line 1',
            manual_company_address_line_2='Line 2',
            manual_company_address_town='Town 1',
            manual_company_address_county='County 1',
            manual_company_address_postcode='ZZ1 8ZZ',
            manual_time_trading_in_uk=ManualCompanyDetailsForm.TimeTradingInUk.TWO_TO_FIVE_YEARS,
            manual_registration_number=None,
            manual_vat_number=None,
            manual_website=None,
            company=None
        )
