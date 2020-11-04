from unittest.mock import patch

from bs4 import BeautifulSoup
from django.urls import reverse

from web.grant_applications.forms import CompanyDetailsForm
from web.grant_applications.services import BackofficeService
from web.grant_applications.views import CompanyDetailsView
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import (
    FAKE_GRANT_APPLICATION, FAKE_COMPANY
)
from web.tests.helpers.testcases import BaseTestCase


@patch.object(BackofficeService, 'create_company', return_value=FAKE_COMPANY)
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestCompanyDetailsView(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:company-details', args=(self.gal.pk,))

    def test_get_template(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, CompanyDetailsView.template_name)

    def test_back_url_select_company(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        back_html = BeautifulSoup(response.content, 'html.parser').find(id='id_back_link')
        self.assertEqual(
            back_html.attrs['href'],
            reverse('grant-applications:select-company', args=(self.gal.pk,))
        )

    def test_back_url_manual_company_details(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['company'] = None
        mocks[1].return_value = fake_grant_application

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        back_html = BeautifulSoup(response.content, 'html.parser').find(id='id_back_link')
        self.assertEqual(
            back_html.attrs['href'],
            reverse('grant-applications:manual-company-details', args=(self.gal.pk,))
        )

    def test_post(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'number_of_employees': CompanyDetailsForm.NumberOfEmployees.HAS_FEWER_THAN_10,
                'is_turnover_greater_than': True
            }
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            number_of_employees=CompanyDetailsForm.NumberOfEmployees.HAS_FEWER_THAN_10.value,
            is_turnover_greater_than=True
        )

    def test_post_form_redirect_path(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'number_of_employees': CompanyDetailsForm.NumberOfEmployees.HAS_FEWER_THAN_10,
                'is_turnover_greater_than': True
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response=response,
            expected_url=reverse('grant-applications:contact-details', args=(self.gal.pk,))
        )

    def test_post_cannot_set_random_field(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'number_of_employees': CompanyDetailsForm.NumberOfEmployees.HAS_FEWER_THAN_10,
                'is_turnover_greater_than': True,
                'is_already_committed_to_event': True
            }
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            number_of_employees=CompanyDetailsForm.NumberOfEmployees.HAS_FEWER_THAN_10.value,
            is_turnover_greater_than=True
        )

    def test_get_redirects_to_confirmation_if_application_already_sent_for_review(self, *mocks):
        self.gal.sent_for_review = True
        self.gal.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )

    def test_required_fields(self, *mocks):
        response = self.client.post(self.url)
        self.assertFormError(response, 'form', 'number_of_employees', self.form_msgs['required'])
        self.assertFormError(
            response, 'form', 'is_turnover_greater_than', self.form_msgs['required']
        )
