from unittest.mock import patch

from django.urls import reverse

from web.grant_applications.services import BackofficeService
from web.grant_applications.views import ContactDetailsView
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import (
    FAKE_GRANT_APPLICATION, FAKE_EVENT, FAKE_SECTOR
)
from web.tests.helpers.testcases import BaseTestCase


@patch.object(BackofficeService, 'list_sectors', return_value=[FAKE_SECTOR])
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'list_trade_events', return_value=[FAKE_EVENT])
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestContactDetailsView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:contact-details', kwargs={'pk': self.gal.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ContactDetailsView.template_name)

    def test_post_redirects(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'applicant_full_name': 'A Name',
                'applicant_email': 'test@test.com',
                'applicant_mobile_number': '+447777777777',
                'job_title': 'director'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response=response,
            expected_url=reverse(ContactDetailsView.success_url_name, kwargs={'pk': self.gal.pk})
        )

    def test_required_fields(self, *mocks):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        msg = 'This field is required.'
        self.assertFormError(response, 'form', 'applicant_full_name', msg)
        self.assertFormError(response, 'form', 'applicant_email', msg)
        self.assertFormError(response, 'form', 'applicant_mobile_number', msg)
        self.assertFormError(response, 'form', 'job_title', msg)

    def test_post_data_is_saved(self, *mocks):
        self.client.post(
            self.url,
            data={
                'applicant_full_name': 'A Name',
                'applicant_email': 'test@test.com',
                'applicant_mobile_number': '07777777777',
                'job_title': 'director'
            }
        )
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            applicant_full_name='A Name',
            applicant_email='test@test.com',
            applicant_mobile_number='+447777777777',
            job_title='director'
        )

    def test_mobile_must_be_gb_number_international(self, *mocks):
        response = self.client.post(self.url, data={'applicant_mobile_number': '+457777777777'})
        self.assertFormError(
            response, 'form', 'applicant_mobile_number',
            "Enter a valid phone number (e.g. 0121 234 5678) or a number with an international "
            "call prefix."
        )

    def test_mobile_must_be_gb_number_national(self, *mocks):
        response = self.client.post(self.url, data={'applicant_mobile_number': '2025550154'})
        self.assertFormError(
            response, 'form', 'applicant_mobile_number',
            "Enter a valid phone number (e.g. 0121 234 5678) or a number with an international "
            "call prefix."
        )

    def test_get_redirects_to_confirmation_if_application_already_sent_for_review(self, *mocks):
        self.gal.sent_for_review = True
        self.gal.save()
        response = self.client.get(self.url)
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )

    def test_get_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_active'] = False
        mocks[2].return_value = fake_grant_application
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))

    def test_post_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_active'] = False
        mocks[2].return_value = fake_grant_application
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))
