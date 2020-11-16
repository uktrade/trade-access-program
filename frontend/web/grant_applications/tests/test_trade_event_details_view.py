from unittest.mock import patch

from bs4 import BeautifulSoup
from django.urls import reverse

from web.grant_applications.services import BackofficeService
from web.grant_applications.views import TradeEventDetailsView
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import FAKE_GRANT_APPLICATION
from web.tests.helpers.testcases import BaseTestCase


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestTradeEventDetailsView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:trade-event-details', kwargs={'pk': self.gal.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TradeEventDetailsView.template_name)

    def test_back_url_export_details(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['has_exported_before'] = True
        mocks[1].return_value = fake_grant_application

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        back_html = BeautifulSoup(response.content, 'html.parser').find(id='id_back_link')
        self.assertEqual(
            back_html.attrs['href'],
            reverse('grant-applications:export-details', args=(self.gal.pk,))
        )

    def test_back_url_export_experience(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['has_exported_before'] = False
        mocks[1].return_value = fake_grant_application

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        back_html = BeautifulSoup(response.content, 'html.parser').find(id='id_back_link')
        self.assertEqual(
            back_html.attrs['href'],
            reverse('grant-applications:export-experience', args=(self.gal.pk,))
        )

    def test_post(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'interest_in_event_description': 'A description',
                'is_in_contact_with_tcp': True,
                'tcp_name': 'A Person',
                'tcp_email': 'tcp@test.com',
                'tcp_mobile_number': '07777777777',
                'is_intending_to_exhibit_as_tcp_stand': True,
                'stand_trade_name': 'A name',
                'trade_show_experience_description': 'Some experience',
                'additional_guidance': 'Some additional guidance'
            }
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            interest_in_event_description='A description',
            is_in_contact_with_tcp=True,
            tcp_name='A Person',
            tcp_email='tcp@test.com',
            tcp_mobile_number='+447777777777',
            is_intending_to_exhibit_as_tcp_stand=True,
            stand_trade_name='A name',
            trade_show_experience_description='Some experience',
            additional_guidance='Some additional guidance'
        )

    def test_required_fields(self, *mocks):
        response = self.client.post(self.url)
        msg = self.form_msgs['required']
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'interest_in_event_description', msg)
        self.assertFormError(response, 'form', 'is_in_contact_with_tcp', msg)
        self.assertFormError(response, 'form', 'is_intending_to_exhibit_as_tcp_stand', msg)
        self.assertFormError(response, 'form', 'stand_trade_name', msg)
        self.assertFormError(response, 'form', 'trade_show_experience_description', msg)
        self.assertFormError(response, 'form', 'additional_guidance', msg)

    def test_conditionally_required_field_errors(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'is_in_contact_with_tcp': True
            }
        )
        msg = self.form_msgs['required']
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'tcp_name', msg)
        self.assertFormError(response, 'form', 'tcp_email', msg)
        self.assertFormError(response, 'form', 'tcp_mobile_number', msg)

    def test_conditionally_optional_fields_not_present(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'interest_in_event_description': 'A description',
                'is_in_contact_with_tcp': False,
                'is_intending_to_exhibit_as_tcp_stand': True,
                'stand_trade_name': 'A name',
                'trade_show_experience_description': 'Some experience',
                'additional_guidance': 'Some additional guidance'
            }
        )
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            interest_in_event_description='A description',
            is_in_contact_with_tcp=False,
            is_intending_to_exhibit_as_tcp_stand=True,
            stand_trade_name='A name',
            trade_show_experience_description='Some experience',
            additional_guidance='Some additional guidance',
            # Optional fields all explicitly set to None to overwrite any previously set value
            tcp_name=None,
            tcp_email=None,
            tcp_mobile_number=None,
        )
        self.assertRedirects(
            response,
            reverse('grant-applications:state-aid-summary', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )

    def test_conditionally_optional_fields_present(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'interest_in_event_description': 'A description',
                'is_in_contact_with_tcp': False,
                'tcp_name': 'A Person',
                'tcp_email': 'tcp@test.com',
                'tcp_mobile_number': '07777777777',
                'is_intending_to_exhibit_as_tcp_stand': True,
                'stand_trade_name': 'A name',
                'trade_show_experience_description': 'Some experience',
                'additional_guidance': 'Some additional guidance'
            }
        )
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            interest_in_event_description='A description',
            is_in_contact_with_tcp=False,
            is_intending_to_exhibit_as_tcp_stand=True,
            stand_trade_name='A name',
            trade_show_experience_description='Some experience',
            additional_guidance='Some additional guidance',
            # Optional fields all explicitly set to None to overwrite any previously set value
            tcp_name=None,
            tcp_email=None,
            tcp_mobile_number=None,
        )
        self.assertRedirects(
            response,
            reverse('grant-applications:state-aid-summary', args=(self.gal.pk,)),
            fetch_redirect_response=False
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
        fake_grant_application['is_active'] = False
        mocks[1].return_value = fake_grant_application
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))

    def test_post_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_active'] = False
        mocks[1].return_value = fake_grant_application
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))

    def test_get_does_not_redirect_to_ineligible_if_review_page_has_been_viewed(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_active'] = False
        mocks[1].return_value = fake_grant_application

        self.gal.has_viewed_review_page = True
        self.gal.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TradeEventDetailsView.template_name)
