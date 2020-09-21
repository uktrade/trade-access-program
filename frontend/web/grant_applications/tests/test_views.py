from datetime import timedelta
from unittest.mock import patch

from dateutil.utils import today
from django.urls import reverse, resolve
from django.utils.datetime_safe import date
from django.utils.http import urlencode

from web.grant_applications.forms import BusinessInformationForm
from web.grant_applications.models import GrantApplicationLink
from web.grant_applications.services import BackofficeServiceException, BackofficeService
from web.grant_applications.tests.factories.grant_application_link import (
    GrantApplicationLinkFactory
)
from web.grant_applications.views import (
    SearchCompanyView, SelectCompanyView, AboutYourBusinessView, AboutYouView, AboutTheEventView,
    PreviousApplicationsView, EventIntentionView, BusinessInformationView, ExportExperienceView,
    StateAidView, ApplicationReviewView
)
from web.tests.helpers.backoffice_objects import FAKE_GRANT_APPLICATION, FAKE_COMPANY, \
    FAKE_GRANT_MANAGEMENT_PROCESS, FAKE_FLATTENED_GRANT_APPLICATION
from web.tests.helpers.testcases import BaseTestCase


@patch.object(
    BackofficeService, 'search_companies',
    return_value=[{
        'primary_name': FAKE_GRANT_APPLICATION['company']['name'],
        'duns_number': str(FAKE_GRANT_APPLICATION['company']['duns_number'])
    }]
)
@patch('web.grant_applications.forms.BackofficeService', autospec=True)
class TestSearchCompanyView(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('grant_applications:search-company')

    def test_search_company_get_template(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, SearchCompanyView.template_name)

    def test_search_term_required(self, *mocks):
        response = self.client.post(self.url)
        self.assertFormError(response, 'form', 'search_term', 'This field is required.')

    def test_search_company_saves_backoffice_ga_id(self, *mocks):
        response = self.client.post(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(GrantApplicationLink.objects.filter(search_term='company-1').exists())

    def test_search_company_post_form_redirect_path(self, *mocks):
        response = self.client.post(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, 302)
        gal = GrantApplicationLink.objects.get(search_term='company-1')
        self.assertRedirects(
            response,
            expected_url=reverse('grant_applications:select-company', kwargs={'pk': gal.pk})
        )

    def test_search_company_post_form_redirect_template(self, *mocks):
        response = self.client.post(self.url, data={'search_term': 'company-1'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, SelectCompanyView.template_name)


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'list_companies', return_value=[FAKE_COMPANY])
@patch.object(BackofficeService, 'create_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(
    BackofficeService, 'search_companies',
    return_value=[{
        'primary_name': FAKE_GRANT_APPLICATION['company']['name'],
        'duns_number': str(FAKE_GRANT_APPLICATION['company']['duns_number'])
    }]
)
class TestSelectCompanyView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory(
            search_term='company',
            backoffice_grant_application_id=None
        )
        self.url = reverse('grant_applications:select-company', kwargs={'pk': self.gal.pk})

    def test_get_template(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, SelectCompanyView.template_name)
        mocks[0].assert_called_once_with(search_term=self.gal.search_term)
        self.assertIn(FAKE_GRANT_APPLICATION['company']['name'], response.content.decode())

    def test_get_template_on_backoffice_service_exception(self, *mocks):
        mocks[0].side_effect = [BackofficeServiceException]
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(FAKE_GRANT_APPLICATION['company']['name'], response.content.decode())
        self.assertIn('Choice not listed', response.content.decode())

    def test_post_required_fields(self, *mocks):
        response = self.client.post(self.url)
        self.assertFormError(response, 'form', 'duns_number', 'This field is required.')

    def test_post_form_redirect_path(self, *mocks):
        response = self.client.post(
            self.url, data={'duns_number': FAKE_GRANT_APPLICATION['company']['duns_number']}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            expected_url=reverse('grant_applications:about-your-business', args=(self.gal.pk,))
        )

    def test_post_form_redirect_template(self, *mocks):
        response = self.client.post(
            self.url,
            {'duns_number': FAKE_GRANT_APPLICATION['company']['duns_number']},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AboutYourBusinessView.template_name)

    def test_post_creates_company_backoffice_grant_application(self, *mocks):
        response = self.client.post(
            self.url, data={'duns_number': FAKE_GRANT_APPLICATION['company']['duns_number']}
        )
        self.assertEqual(response.status_code, 302)

        self.gal.refresh_from_db()
        self.assertEqual(
            str(self.gal.backoffice_grant_application_id), FAKE_GRANT_APPLICATION['id']
        )
        mocks[1].assert_called_once_with(
            company_id=FAKE_COMPANY['id'], search_term=self.gal.search_term
        )

    def test_post_backoffice_service_exception(self, *mocks):
        mocks[1].side_effect = [BackofficeServiceException]
        response = self.client.post(
            self.url,
            data={'duns_number': FAKE_GRANT_APPLICATION['company']['duns_number']},
            follow=True
        )
        self.assertFormError(
            response, 'form', None, 'An unexpected error occurred. Please resubmit the form.'
        )
        self.gal.refresh_from_db()
        self.assertIsNone(self.gal.backoffice_grant_application_id)


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestAboutYourBusinessView(BaseTestCase):
    table_row_html = '<th scope="row" class="govuk-table__header">{header}</th>\n      ' \
                     '<td class="govuk-table__cell">{value}</td>'

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant_applications:about-your-business', kwargs={'pk': self.gal.pk})
        self.tomorrow = today() + timedelta(days=1)

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AboutYourBusinessView.template_name)

        self.assertInHTML(
            self.table_row_html.format(
                header='Company Name', value=FAKE_GRANT_APPLICATION['company']['name']
            ),
            response.content.decode()
        )
        self.assertInHTML(
            self.table_row_html.format(
                header='Dun and Bradstreet Number',
                value=FAKE_GRANT_APPLICATION['company']['duns_number']
            ),
            response.content.decode()
        )
        self.assertInHTML(
            self.table_row_html.format(
                header='Previous Applications',
                value=FAKE_GRANT_APPLICATION['company']['previous_applications']
            ),
            response.content.decode()
        )
        self.assertInHTML(
            self.table_row_html.format(
                header='Applications in Review',
                value=FAKE_GRANT_APPLICATION['company']['applications_in_review']
            ),
            response.content.decode()
        )

    def test_post_redirects(self, *mocks):
        response = self.client.post(self.url, content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 302)

    def test_post_redirect_template(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AboutYouView.template_name)
        self.assertRedirects(
            response=response,
            expected_url=reverse('grant_applications:about-you', kwargs={'pk': self.gal.pk})
        )


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(
    BackofficeService, 'list_trade_events',
    return_value=[{'id': '235678a7-b3ff-4256-b6ae-ce7ddb4d18gg', 'display_name': 'An Event'}]
)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestAboutYouView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant_applications:about-you', kwargs={'pk': self.gal.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AboutYouView.template_name)

    def test_post_redirects(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'applicant_full_name': 'A Name',
                'applicant_email': 'test@test.com',
            })
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response=response,
            expected_url=reverse('grant_applications:about-the-event', kwargs={'pk': self.gal.pk})
        )

    def test_post_data_is_saved(self, *mocks):
        self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'applicant_full_name': 'A Name',
                'applicant_email': 'test@test.com',
            })
        )
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            applicant_full_name='A Name',
            applicant_email='test@test.com'
        )


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(
    BackofficeService, 'list_trade_events',
    return_value=[{'id': '235678a7-b3ff-4256-b6ae-ce7ddb4d18gg', 'display_name': 'An Event'}]
)
class TestAboutTheEventView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant_applications:about-the-event', kwargs={'pk': self.gal.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AboutTheEventView.template_name)

    def test_post_redirects(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'event': '235678a7-b3ff-4256-b6ae-ce7ddb4d18gg',
                'is_already_committed_to_event': True,
                'is_intending_on_other_financial_support': True,
            })
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response=response, expected_url=reverse(
                'grant_applications:previous-applications', kwargs={'pk': self.gal.pk}
            )
        )

    def test_post_data_is_saved(self, *mocks):
        self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'event': '235678a7-b3ff-4256-b6ae-ce7ddb4d18gg',
                'is_already_committed_to_event': True,
                'is_intending_on_other_financial_support': False,
            })
        )
        mocks[1].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            is_already_committed_to_event=True,
            is_intending_on_other_financial_support=False,
            event='235678a7-b3ff-4256-b6ae-ce7ddb4d18gg'
        )

    def test_boolean_fields_must_be_present(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({'event': 1})
        )
        self.assertFormError(
            response, 'form', 'is_already_committed_to_event', 'This field is required.'
        )
        self.assertFormError(
            response, 'form', 'is_intending_on_other_financial_support', 'This field is required.'
        )


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestPreviousApplicationsView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant_applications:previous-applications', kwargs={'pk': self.gal.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, PreviousApplicationsView.template_name)

    def test_post(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'has_previously_applied': False,
                'previous_applications': FAKE_GRANT_APPLICATION['previous_applications']
            })
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            has_previously_applied=False,
            previous_applications=FAKE_GRANT_APPLICATION['previous_applications']
        )

    def test_true_has_previously_applied_gives_0_previous_applications(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'has_previously_applied': True,
            })
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            has_previously_applied=True,
            previous_applications=0
        )

    def test_boolean_field_must_be_present(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({'event': 1})
        )
        self.assertFormError(response, 'form', 'has_previously_applied', 'This field is required.')


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(
    BackofficeService, 'list_sectors',
    return_value=[{'id': 1, 'full_name': 'full-name-1'}, {'id': 2, 'full_name': 'full-name-2'}]
)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestEventIntentionView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant_applications:event-intention', kwargs={'pk': self.gal.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, EventIntentionView.template_name)

    def test_post(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'is_first_exhibit_at_event': False,
                'number_of_times_exhibited_at_event': 1,
            })
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            is_first_exhibit_at_event=False,
            number_of_times_exhibited_at_event=1
        )

    def test_true_is_first_exhibit_at_event_gives_0_number_of_times_exhibited(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'is_first_exhibit_at_event': True,
            })
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            is_first_exhibit_at_event=True,
            number_of_times_exhibited_at_event=0
        )


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(
    BackofficeService, 'list_sectors',
    return_value=[{'id': 1, 'full_name': 'full-name-1'}, {'id': 2, 'full_name': 'full-name-2'}]
)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestBusinessInformationView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant_applications:business-information', kwargs={'pk': self.gal.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, BusinessInformationView.template_name)

    def test_sector_choices_come_from_sector_model(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertInHTML('<option value="1">full-name-1</option>', response.content.decode())
        self.assertInHTML('<option value="2">full-name-2</option>', response.content.decode())

    def test_post(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'goods_and_services_description': 'A description',
                'business_name_at_exhibit': 'A name',
                'turnover': 1234,
                'number_of_employees': BusinessInformationForm.NumberOfEmployees.HAS_FEWER_THAN_10,
                'sector': 1,
                'website': 'www.a-website.com',
            })
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            goods_and_services_description='A description',
            business_name_at_exhibit='A name',
            number_of_employees='fewer-than-10',
            turnover=1234,
            website='http://www.a-website.com',
            sector='1',
        )

    def test_initial_form_data(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertInHTML(
            f'<input type="text" name="business_name_at_exhibit" id="id_business_name_at_exhibit" '
            f'value="{FAKE_GRANT_APPLICATION["business_name_at_exhibit"]}" required '
            f'class="govuk-input govuk-!-width-two-thirds" >',
            response.content.decode()
        )
        self.assertInHTML(
            f'<input type="text" name="turnover" value="{FAKE_GRANT_APPLICATION["turnover"]}" '
            f'class="govuk-input govuk-!-width-one-quarter" required id="id_turnover">',
            response.content.decode()
        )
        self.assertInHTML(
            f'<input class="govuk-radios__input" id="id_number_of_employees_0" checked type="radio"'
            f' name="number_of_employees" value="{FAKE_GRANT_APPLICATION["number_of_employees"]}">',
            response.content.decode()
        )
        self.assertInHTML(
            f'<input type="text" name="website" value="{FAKE_GRANT_APPLICATION["website"]}" '
            f'class="govuk-input govuk-!-width-two-thirds" required '
            f'id="id_website">',
            response.content.decode()
        )

    def test_website_validation(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({'website': 'Not a website'})
        )
        self.assertFormError(response, 'form', 'website', 'Enter a valid URL.')

    def test_get_redirects_to_confirmation_if_application_already_sent_for_review(self, *mocks):
        self.gal.sent_for_review = True
        self.gal.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('grant_applications:confirmation', args=(self.gal.pk,))
        )


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestExportExperienceView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant_applications:export-experience', kwargs={'pk': self.gal.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ExportExperienceView.template_name)

    def test_post(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'has_exported_before': True,
                'is_planning_to_grow_exports': True,
                'is_seeking_export_opportunities': False,
            })
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            has_exported_before=True,
            is_planning_to_grow_exports=True,
            is_seeking_export_opportunities=False
        )


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestStateAidView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant_applications:state-aid', kwargs={'pk': self.gal.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, StateAidView.template_name)

    def test_post(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'has_received_de_minimis_aid': True,
                'de_minimis_aid_public_authority': 'An authority',
                'de_minimis_aid_date_awarded': date(2020, 6, 20),
                'de_minimis_aid_amount': 2000,
                'de_minimis_aid_description': 'A description',
                'de_minimis_aid_recipient': 'A recipient',
                'de_minimis_aid_date_received': date(2020, 6, 25),
            })
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            has_received_de_minimis_aid=True,
            de_minimis_aid_public_authority='An authority',
            de_minimis_aid_date_awarded=date(2020, 6, 20),
            de_minimis_aid_amount=2000,
            de_minimis_aid_description='A description',
            de_minimis_aid_recipient='A recipient',
            de_minimis_aid_date_received=date(2020, 6, 25)
        )

    def test_post_no_aid(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({'has_received_de_minimis_aid': False})
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            has_received_de_minimis_aid=False
        )

    def test_required_fields_when_aid_is_selected(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({'has_received_de_minimis_aid': True})
        )
        self.assertEqual(response.status_code, 200)
        msg = 'This field is required.'
        self.assertFormError(response, 'form', 'de_minimis_aid_public_authority', msg)
        self.assertFormError(response, 'form', 'de_minimis_aid_date_awarded', msg)
        self.assertFormError(response, 'form', 'de_minimis_aid_amount', msg)
        self.assertFormError(response, 'form', 'de_minimis_aid_description', msg)
        self.assertFormError(response, 'form', 'de_minimis_aid_recipient', msg)
        self.assertFormError(response, 'form', 'de_minimis_aid_date_received', msg)

    def test_aid_amount_is_integer(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'has_received_de_minimis_aid': True,
                'de_minimis_aid_amount': 'bad-value',
            })
        )
        self.assertFormError(response, 'form', 'de_minimis_aid_amount', 'Enter a whole number.')


@patch.object(
    BackofficeService, 'get_grant_application', return_value=FAKE_FLATTENED_GRANT_APPLICATION
)
@patch.object(
    BackofficeService, 'send_grant_application_for_review',
    return_value=FAKE_GRANT_MANAGEMENT_PROCESS
)
@patch.object(
    BackofficeService, 'search_companies',
    return_value=[{
        'primary_name': FAKE_GRANT_APPLICATION['company']['name'],
        'duns_number': str(FAKE_GRANT_APPLICATION['company']['duns_number'])
    }]
)
@patch.object(
    BackofficeService, 'list_trade_events',
    return_value=[{'id': '235678a7-b3ff-4256-b6ae-ce7ddb4d18gg', 'display_name': 'An Event'}]
)
@patch.object(
    BackofficeService, 'list_sectors',
    return_value=[{'id': 1, 'full_name': 'full-name-1'}, {'id': 2, 'full_name': 'full-name-2'}]
)
class TestApplicationReviewView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant_applications:application-review', kwargs={'pk': self.gal.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            '<dl class="govuk-summary-list govuk-!-margin-bottom-9">',
            response.content.decode()
        )

    def test_post_redirects(self, *mocks):
        self.client.get(self.url)
        response = self.client.post(self.url, content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 302)
        redirect = resolve(response.url)
        self.assertEqual(redirect.kwargs['pk'], str(self.gal.id))
        self.assertRedirects(
            response, reverse('grant_applications:confirmation', args=(self.gal.pk,))
        )

    def test_post_sets_sent_for_review_flag(self, *mocks):
        self.client.get(self.url)
        self.client.post(self.url, content_type='application/x-www-form-urlencoded')
        self.gal.refresh_from_db()
        self.assertTrue(self.gal.sent_for_review)

    def test_sent_for_review_not_set_on_backoffice_error(self, *mocks):
        mocks[3].side_effect = [BackofficeServiceException]
        self.client.get(self.url)
        response = self.client.post(self.url, follow=True)
        self.assertFormError(
            response, 'form', None, 'An unexpected error occurred. Please resubmit the form.'
        )
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
            response, reverse('grant_applications:confirmation', args=(self.gal.pk,))
        )
