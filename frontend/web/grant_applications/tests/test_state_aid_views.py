import datetime
from decimal import Decimal
from unittest.mock import patch

from bs4 import BeautifulSoup
from django.urls import reverse

from web.grant_applications.services import BackofficeService, BackofficeServiceException
from web.grant_applications.views import StateAidSummaryView, AddStateAidView, EditStateAidView
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import FAKE_GRANT_APPLICATION, FAKE_STATE_AID
from web.tests.helpers.testcases import BaseTestCase


@patch.object(BackofficeService, 'list_state_aids', return_value=[FAKE_STATE_AID])
@patch.object(BackofficeService, 'get_state_aid', return_value=FAKE_STATE_AID)
@patch.object(BackofficeService, 'update_state_aid', return_value=FAKE_STATE_AID)
@patch.object(BackofficeService, 'create_state_aid', return_value=FAKE_STATE_AID)
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestStateAidSummaryView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:state-aid-summary', args=(self.gal.pk,))

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, StateAidSummaryView.template_name)

    def test_get_with_no_state_aid_items_gives_default_table(self, *mocks):
        mocks[5].return_value = []
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        html = BeautifulSoup(response.content, 'html.parser').find(id='id_table')

        all_table_cells = html.find_all('td')
        self.assertEqual(len(all_table_cells), 4)
        for cell in all_table_cells:
            self.assertEqual(cell.text, '\n        -\n      ')

    def test_back_url(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        back_html = BeautifulSoup(response.content, 'html.parser').find(id='id_back_link')
        self.assertEqual(
            back_html.attrs['href'],
            reverse('grant-applications:export-experience', args=(self.gal.pk,))
        )

    def test_add_state_aid_link(self, *mocks):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(
            soup.find(id='id_link_button').attrs['href'],
            reverse('grant-applications:add-state-aid', args=(self.gal.pk,))
        )

    def test_post(self, *mocks):
        response = self.client.post(self.url)
        mocks[0].assert_not_called()
        self.assertRedirects(
            response,
            reverse('grant-applications:application-review', args=(self.gal.pk,)),
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


@patch.object(BackofficeService, 'get_state_aid', return_value=FAKE_STATE_AID)
@patch.object(BackofficeService, 'update_state_aid', return_value=FAKE_STATE_AID)
@patch.object(BackofficeService, 'create_state_aid', return_value=FAKE_STATE_AID)
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestAddStateAidView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:add-state-aid', args=(self.gal.pk,))

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AddStateAidView.template_name)

    def test_post_creates_state_aid_item(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'authority': 'An authority',
                'date_received_0': '01',
                'date_received_1': '05',
                'date_received_2': '2020',
                'amount': 2000,
                'description': 'A description',
            }
        )
        self.assertEqual(response.status_code, 302)
        mocks[2].assert_called_once_with(
            grant_application=str(self.gal.backoffice_grant_application_id),
            authority='An authority',
            date_received=datetime.date(year=2020, month=5, day=1),
            amount=2000,
            description='A description',
        )

    def test_create_state_aid_backoffice_exception(self, *mocks):
        mocks[2].side_effect = BackofficeServiceException
        response = self.client.post(
            self.url,
            data={
                'authority': 'An authority',
                'date_received_0': '01',
                'date_received_1': '05',
                'date_received_2': '2020',
                'amount': 2000,
                'description': 'A description',
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', None, self.form_msgs['resubmit'])
        mocks[2].assert_called_once_with(
            grant_application=str(self.gal.backoffice_grant_application_id),
            authority='An authority',
            date_received=datetime.date(year=2020, month=5, day=1),
            amount=2000,
            description='A description',
        )

    def test_required_fields(self, *mocks):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'authority', self.form_msgs['required'])
        self.assertFormError(response, 'form', 'date_received', self.form_msgs['required'])
        self.assertFormError(response, 'form', 'amount', self.form_msgs['required'])
        self.assertFormError(response, 'form', 'description', self.form_msgs['required'])

    def test_aid_amount_is_a_number(self, *mocks):
        response = self.client.post(self.url, data={'amount': 'bad-value'})
        self.assertFormError(response, 'form', 'amount', self.form_msgs['number'])

    def test_invalid_date_received(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'date_received_0': 'bad',
                'date_received_1': 'bad',
                'date_received_2': 'bad',
            }
        )
        self.assertFormError(response, 'form', 'date_received', self.form_msgs['invalid-date'])

    def test_missing_date_received_year(self, *mocks):
        response = self.client.post(
            self.url, data={'date_received_0': '01', 'date_received_1': '05'}
        )
        self.assertFormError(response, 'form', 'date_received', self.form_msgs['required'])

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


@patch.object(BackofficeService, 'list_state_aids', return_value=[FAKE_STATE_AID])
@patch.object(BackofficeService, 'get_state_aid', return_value=FAKE_STATE_AID)
@patch.object(BackofficeService, 'update_state_aid', return_value=FAKE_STATE_AID)
@patch.object(BackofficeService, 'create_state_aid', return_value=FAKE_STATE_AID)
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestEditStateAidView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse(
            'grant-applications:edit-state-aid',
            kwargs={'pk': self.gal.pk, 'state_aid_pk': FAKE_STATE_AID['id']}
        )

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, EditStateAidView.template_name)

    def test_update_state_aid_backoffice_exception(self, *mocks):
        mocks[3].side_effect = BackofficeServiceException
        response = self.client.post(self.url, data={'amount': 2000})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', None, self.form_msgs['resubmit'])
        mocks[3].assert_called_once_with(state_aid_id=FAKE_STATE_AID['id'], amount=Decimal('2000'))

    def test_edit_amount(self, *mocks):
        response = self.client.post(self.url, data={'amount': 2000})
        self.assertEqual(response.status_code, 302)
        mocks[3].assert_called_once_with(state_aid_id=FAKE_STATE_AID['id'], amount=Decimal('2000'))

    def test_all_fields_optional(self, *mocks):
        response = self.client.post(self.url)
        self.assertRedirects(
            response, reverse('grant_applications:state-aid-summary', args=(self.gal.pk,))
        )

    def test_aid_amount_is_a_number(self, *mocks):
        response = self.client.post(self.url, data={'amount': 'bad-value'})
        self.assertFormError(response, 'form', 'amount', self.form_msgs['number'])

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


@patch.object(BackofficeService, 'delete_state_aid')
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestDeleteStateAidView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse(
            'grant-applications:delete-state-aid',
            kwargs={'pk': self.gal.pk, 'state_aid_pk': FAKE_STATE_AID['id']}
        )

    def test_delete(self, *mocks):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('grant-applications:state-aid-summary', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )
        mocks[1].assert_called_once_with(state_aid_id=FAKE_STATE_AID['id'])

    def test_on_backoffice_exception_redirect_still_happens(self, *mocks):
        mocks[1].side_effect = BackofficeServiceException
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('grant-applications:state-aid-summary', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )
        mocks[1].assert_called_once_with(state_aid_id=FAKE_STATE_AID['id'])

    def test_get_redirects_to_confirmation_if_application_already_sent_for_review(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['sent_for_review'] = True
        mocks[0].return_value = fake_grant_application
        response = self.client.get(self.url)
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )

    def test_get_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_active'] = False
        mocks[0].return_value = fake_grant_application
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))

    def test_post_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_active'] = False
        mocks[0].return_value = fake_grant_application
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))


@patch.object(BackofficeService, 'get_state_aid', return_value=FAKE_STATE_AID)
@patch.object(BackofficeService, 'create_state_aid', return_value=FAKE_STATE_AID)
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestDuplicateStateAidView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse(
            'grant-applications:duplicate-state-aid',
            kwargs={'pk': self.gal.pk, 'state_aid_pk': FAKE_STATE_AID['id']}
        )

    def test_duplicate(self, *mocks):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('grant-applications:state-aid-summary', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )
        mocks[1].assert_called_once_with(
            grant_application=self.gal.backoffice_grant_application_id,
            authority=FAKE_STATE_AID['authority'],
            amount=FAKE_STATE_AID['amount'],
            description=FAKE_STATE_AID['description'],
            date_received=FAKE_STATE_AID['date_received']
        )

    def test_on_get_backoffice_exception_redirect_still_happens(self, *mocks):
        mocks[2].side_effect = BackofficeServiceException
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('grant-applications:state-aid-summary', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )
        mocks[2].assert_called_once_with(state_aid_id=FAKE_STATE_AID['id'])

    def test_on_create_backoffice_exception_redirect_still_happens(self, *mocks):
        mocks[1].side_effect = BackofficeServiceException
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('grant-applications:state-aid-summary', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )
        mocks[1].assert_called_once_with(
            grant_application=self.gal.backoffice_grant_application_id,
            authority=FAKE_STATE_AID['authority'],
            amount=FAKE_STATE_AID['amount'],
            description=FAKE_STATE_AID['description'],
            date_received=FAKE_STATE_AID['date_received']
        )

    def test_get_redirects_to_confirmation_if_application_already_sent_for_review(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['sent_for_review'] = True
        mocks[0].return_value = fake_grant_application
        response = self.client.get(self.url)
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )

    def test_get_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_active'] = False
        mocks[0].return_value = fake_grant_application
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))

    def test_post_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_active'] = False
        mocks[0].return_value = fake_grant_application
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))
