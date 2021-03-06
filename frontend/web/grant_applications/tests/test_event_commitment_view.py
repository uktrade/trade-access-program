from unittest.mock import patch

from django.urls import reverse

from web.grant_applications.services import BackofficeService
from web.grant_applications.views import EventCommitmentView
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import FAKE_GRANT_APPLICATION
from web.tests.helpers.testcases import BaseTestCase


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestEventCommitmentView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:event-commitment', args=(self.gal.pk,))

    def test_get_template(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, EventCommitmentView.template_name)

    def test_post_redirects(self, *mocks):
        response = self.client.post(self.url, data={'is_already_committed_to_event': True})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response=response,
            expected_url=reverse(EventCommitmentView.success_url_name, args=(self.gal.pk,))
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
        self.assertTemplateUsed(response, EventCommitmentView.template_name)

    def test_post_redirects_to_review_page_if_application_review_page_has_been_viewed(self, *mocks):
        self.gal.has_viewed_review_page = True
        self.gal.save()
        response = self.client.post(self.url, data={'is_already_committed_to_event': True})
        self.assertRedirects(
            response,
            reverse('grant-applications:application-review', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )

    def test_post_data_is_saved(self, *mocks):
        self.client.post(self.url, data={'is_already_committed_to_event': True})
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            is_already_committed_to_event=True
        )

    def test_boolean_fields_must_be_present(self, *mocks):
        response = self.client.post(self.url)
        self.assertFormError(
            response, 'form', 'is_already_committed_to_event', self.form_msgs['required']
        )
