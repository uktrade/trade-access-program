from unittest.mock import patch

from django.urls import reverse

from web.grant_applications.services import BackofficeService
from web.grant_applications.views import ExportDetailsView
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import FAKE_GRANT_APPLICATION
from web.tests.helpers.testcases import BaseTestCase


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestExportDetailsView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:export-details', kwargs={'pk': self.gal.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ExportDetailsView.template_name)

    def test_post(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'has_exported_in_last_12_months': True,
                'export_regions': ['africa', 'north america'],
                'markets_intending_on_exporting_to': ['existing', 'new'],
                'in_contact_with_dit_trade_advisor': True,
                'export_experience_description': 'A description',
                'export_strategy': 'A strategy'
            }
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            has_exported_in_last_12_months=True,
            export_regions=['africa', 'north america'],
            markets_intending_on_exporting_to=['existing', 'new'],
            in_contact_with_dit_trade_advisor=True,
            export_experience_description='A description',
            export_strategy='A strategy'
        )

    def test_required_fields(self, *mocks):
        response = self.client.post(self.url)
        msg = self.form_msgs['required']
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'has_exported_in_last_12_months', msg)
        self.assertFormError(response, 'form', 'export_regions', msg)
        self.assertFormError(response, 'form', 'markets_intending_on_exporting_to', msg)
        self.assertFormError(response, 'form', 'in_contact_with_dit_trade_advisor', msg)
        self.assertFormError(response, 'form', 'export_experience_description', msg)
        self.assertFormError(response, 'form', 'export_strategy', msg)

    def test_multiple_choice_fields_mixed_valid_invalid_choices(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'export_regions': ['north america', 'bad region'],
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, 'form', 'export_regions',
            self.form_msgs['invalid-choice'].format('bad region')
        )
