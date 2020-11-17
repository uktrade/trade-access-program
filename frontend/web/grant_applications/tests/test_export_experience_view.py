from unittest.mock import patch

from django.urls import reverse

from web.grant_applications.services import BackofficeService
from web.grant_applications.views import ExportExperienceView
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import FAKE_GRANT_APPLICATION
from web.tests.helpers.testcases import BaseTestCase


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestExportExperienceView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:export-experience', kwargs={'pk': self.gal.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ExportExperienceView.template_name)

    def test_post(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'has_exported_before': False,
                'has_product_or_service_for_export': True,
            }
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            has_exported_before=False,
            has_product_or_service_for_export=True,
            # we expect this screen to clear the export details if has_exported_before is False
            has_exported_in_last_12_months=None,
            export_regions=None,
            markets_intending_on_exporting_to=None,
            is_in_contact_with_dit_trade_advisor=None,
            ita_name=None,
            ita_email=None,
            ita_mobile_number=None,
            export_experience_description=None,
            export_strategy=None,
        )

    def test_post_redirect_to_export_details_on_true(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['has_exported_before'] = True
        mocks[0].return_value = fake_grant_application
        response = self.client.post(self.url, data={'has_exported_before': True})
        self.assertRedirects(
            response,
            reverse('grant-applications:export-details', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )

    def test_post_redirect_to_trade_event_details_on_false(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'has_exported_before': False,
                'has_product_or_service_for_export': True,
            }
        )
        self.assertRedirects(
            response,
            reverse('grant-applications:trade-event-details', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )

    def test_2nd_question_not_required_if_has_exported_before_is_true(self, *mocks):
        response = self.client.post(self.url, data={'has_exported_before': True})
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            has_exported_before=True,
            has_product_or_service_for_export=None
        )

    def test_has_exported_before_is_true_has_product_or_service_for_export_is_unset_1(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'has_exported_before': True,
                'has_product_or_service_for_export': True
            }
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            has_exported_before=True,
            has_product_or_service_for_export=None
        )

    def test_has_exported_before_is_true_has_product_or_service_for_export_is_unset_2(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'has_exported_before': True,
                'has_product_or_service_for_export': False
            }
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            has_exported_before=True,
            has_product_or_service_for_export=None
        )

    def test_2nd_question_required_if_has_exported_before_is_false(self, *mocks):
        response = self.client.post(self.url, data={'has_exported_before': False})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, 'form', 'has_product_or_service_for_export', self.form_msgs['required']
        )

    def test_get_redirects_to_confirmation_if_application_already_sent_for_review(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['sent_for_review'] = True
        mocks[1].return_value = fake_grant_application
        response = self.client.get(self.url)
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )

    def test_get_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_eligible'] = False
        mocks[1].return_value = fake_grant_application
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))

    def test_post_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_eligible'] = False
        mocks[1].return_value = fake_grant_application
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))

    def test_get_does_not_redirect_to_ineligible_if_review_page_has_been_viewed(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_eligible'] = False
        mocks[1].return_value = fake_grant_application

        self.gal.has_viewed_review_page = True
        self.gal.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ExportExperienceView.template_name)

    def test_post_redirects_to_review_page_if_application_review_page_has_been_viewed(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['has_exported_before'] = False
        mocks[0].return_value = fake_grant_application
        mocks[1].return_value = fake_grant_application

        self.gal.has_viewed_review_page = True
        self.gal.save()

        response = self.client.post(
            self.url,
            data={
                'has_exported_before': False,
                'has_product_or_service_for_export': True,
            }
        )
        self.assertRedirects(
            response,
            reverse('grant-applications:application-review', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )

    def test_post_redirects_to_export_page_if_application_review_page_has_been_viewed(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['has_exported_before'] = True
        mocks[0].return_value = fake_grant_application
        mocks[1].return_value = fake_grant_application

        self.gal.has_viewed_review_page = True
        self.gal.save()

        response = self.client.post(
            self.url,
            data={
                'has_exported_before': True,
            }
        )
        self.assertRedirects(
            response,
            reverse('grant-applications:export-details', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )
