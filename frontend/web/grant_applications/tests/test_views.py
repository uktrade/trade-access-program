from unittest.mock import patch

from django.urls import reverse, resolve

from web.grant_applications.services import BackofficeServiceException, BackofficeService
from web.grant_applications.views import ApplicationReviewView, EligibilityReviewView
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import (
    FAKE_GRANT_APPLICATION, FAKE_GRANT_MANAGEMENT_PROCESS,
    FAKE_FLATTENED_GRANT_APPLICATION, FAKE_EVENT, FAKE_SEARCH_COMPANIES
)
from web.tests.helpers.testcases import BaseTestCase


@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestEligibilityReviewView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:eligibility-review', args=(self.gal.pk,))

    @patch.object(
        BackofficeService, 'get_grant_application',
        side_effect=[
            FAKE_GRANT_APPLICATION, FAKE_FLATTENED_GRANT_APPLICATION,
            FAKE_FLATTENED_GRANT_APPLICATION
        ]
    )
    def test_get_template(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, EligibilityReviewView.template_name)

    @patch.object(
        BackofficeService, 'get_grant_application',
        side_effect=[
            FAKE_GRANT_APPLICATION, FAKE_FLATTENED_GRANT_APPLICATION,
            FAKE_FLATTENED_GRANT_APPLICATION
        ]
    )
    def test_summary_lists(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('summary_lists', response.context_data)

    @patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
    def test_post(self, *mocks):
        self.client.post(self.url)
        mocks[1].assert_not_called()

    @patch.object(
        BackofficeService, 'get_grant_application',
        side_effect=[FAKE_GRANT_APPLICATION, FAKE_GRANT_APPLICATION]
    )
    def test_post_redirects(self, *mocks):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            expected_url=reverse(EligibilityReviewView.success_url_name, args=(self.gal.pk,)),
            fetch_redirect_response=False
        )


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(
    BackofficeService, 'send_grant_application_for_review',
    return_value=FAKE_GRANT_MANAGEMENT_PROCESS
)
@patch.object(BackofficeService, 'search_companies', return_value=FAKE_SEARCH_COMPANIES)
@patch.object(BackofficeService, 'list_trade_events', return_value=[FAKE_EVENT])
@patch.object(
    BackofficeService, 'list_sectors',
    return_value=[{'id': 1, 'full_name': 'full-name-1'}, {'id': 2, 'full_name': 'full-name-2'}]
)
class TestApplicationReviewView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:application-review', kwargs={'pk': self.gal.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('<dl class="govuk-summary-list">', response.content.decode())

    def test_post_redirects(self, *mocks):
        self.client.get(self.url)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        redirect = resolve(response.url)
        self.assertEqual(redirect.kwargs['pk'], str(self.gal.id))
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )

    def test_sent_for_review(self, *mocks):
        self.client.get(self.url)
        self.client.post(self.url)
        self.gal.refresh_from_db()
        self.assertTrue(self.gal.sent_for_review)
        self.assertIn('application_summary', self.client.session)
        mocks[3].assert_called_once_with(
            str(self.gal.backoffice_grant_application_id),
            application_summary=self.client.session['application_summary']
        )

    def test_sent_for_review_not_set_on_backoffice_error(self, *mocks):
        mocks[3].side_effect = BackofficeServiceException
        self.client.get(self.url)
        response = self.client.post(self.url, follow=True)
        self.assertFormError(response, 'form', None, self.form_msgs['resubmit'])
        self.gal.refresh_from_db()
        self.assertFalse(self.gal.sent_for_review)

        response = self.client.get(self.url)
        self.assertTemplateUsed(response, ApplicationReviewView.template_name)

    def test_get_redirects_to_confirmation_if_application_already_sent_for_review(self, *mocks):
        self.gal.sent_for_review = True
        self.gal.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )
