from unittest import skip
from unittest.mock import patch

from bs4 import BeautifulSoup
from django.urls import reverse, resolve
from django.utils.datetime_safe import date
from django.utils.http import urlencode

from web.grant_applications.forms import BusinessDetailsForm
from web.grant_applications.models import GrantApplicationLink
from web.grant_applications.services import BackofficeServiceException, BackofficeService
from web.grant_applications.views import (
    SearchCompanyView, SelectCompanyView, AboutYouView, AboutTheEventView,
    PreviousApplicationsView, EventIntentionView, BusinessInformationView, ExportExperienceView,
    StateAidView, ApplicationReviewView, EligibilityReviewView, EventFinanceView,
    EligibilityConfirmationView, BusinessDetailsView
)
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import (
    FAKE_GRANT_APPLICATION, FAKE_COMPANY,
    FAKE_GRANT_MANAGEMENT_PROCESS, FAKE_FLATTENED_GRANT_APPLICATION, FAKE_EVENT, FAKE_SECTOR,
    FAKE_SEARCH_COMPANIES
)
from web.tests.helpers.testcases import BaseTestCase, LogCaptureMixin


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'create_company', return_value=FAKE_COMPANY)
@patch.object(BackofficeService, 'list_companies', return_value=[FAKE_COMPANY])
@patch.object(BackofficeService, 'search_companies', return_value=FAKE_SEARCH_COMPANIES)
@patch.object(BackofficeService, 'create_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestSearchCompanyView(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('grant-applications:search-company')

    def test_search_company_get_template(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, SearchCompanyView.template_name)

    def test_back_url(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        back_html = BeautifulSoup(response.content, 'html.parser').find(id='id_back_link')
        self.assertEqual(back_html.attrs['href'], reverse("grant-applications:index"))

    def test_search_term_required(self, *mocks):
        response = self.client.post(self.url)
        self.assertFormError(response, 'form', 'search_term', self.form_msgs['required'])

    def test_search_company_saves_search_term(self, *mocks):
        response = self.client.post(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(GrantApplicationLink.objects.filter(search_term='company-1').exists())

    def test_post_creates_backoffice_grant_application(self, *mocks):
        response = self.client.post(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            GrantApplicationLink.objects.filter(
                backoffice_grant_application_id=FAKE_GRANT_APPLICATION['id']
            ).exists()
        )
        mocks[0].assert_called_once_with(search_term='company-1')

    def test_form_error_on_backoffice_exception(self, *mocks):
        mocks[0].side_effect = [BackofficeServiceException]
        response = self.client.post(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, 200)
        mocks[0].assert_called_once_with(search_term='company-1')
        self.assertFormError(response, 'form', None, self.form_msgs['resubmit'])

    def test_search_company_post_form_redirect_path(self, *mocks):
        response = self.client.post(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, 302)
        gal = GrantApplicationLink.objects.get(search_term='company-1')
        self.assertRedirects(
            response,
            expected_url=reverse('grant-applications:select-company', kwargs={'pk': gal.pk})
        )

    def test_search_company_post_form_redirect_template(self, *mocks):
        response = self.client.post(self.url, data={'search_term': 'company-1'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, SelectCompanyView.template_name)


@patch.object(BackofficeService, 'create_company', return_value=FAKE_COMPANY)
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'list_companies', return_value=[FAKE_COMPANY])
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'search_companies', return_value=FAKE_SEARCH_COMPANIES)
class TestSelectCompanyView(LogCaptureMixin, BaseTestCase):

    def setUp(self):
        super().setUp()
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:select-company', args=(self.gal.pk,))

    def test_get_template(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, SelectCompanyView.template_name)
        mocks[0].assert_called_once_with(search_term=self.gal.search_term)
        self.assertIn(FAKE_GRANT_APPLICATION['company']['name'], response.content.decode())

    def test_details_not_listed(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        link_html = BeautifulSoup(response.content, 'html.parser').find(id='id_details_not_listed')
        self.assertEqual(
            link_html.attrs['href'],
            reverse('grant-applications:business-details', args=(self.gal.pk,))
        )

    @skip("TODO: confirm with design what to display when no company found.")
    def test_get_template_when_no_company_found(self, *mocks):
        mocks[0].return_value = []
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('TODO', response.content.decode())

    def test_get_template_on_backoffice_service_exception(self, *mocks):
        mocks[0].side_effect = [BackofficeServiceException]
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(FAKE_GRANT_APPLICATION['company']['name'], response.content.decode())

    def test_post_required_fields(self, *mocks):
        response = self.client.post(self.url)
        self.assertFormError(response, 'form', 'duns_number', self.form_msgs['required'])

    def test_post_form_redirect_path(self, *mocks):
        response = self.client.post(
            self.url, data={'duns_number': FAKE_GRANT_APPLICATION['company']['duns_number']}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response=response,
            expected_url=reverse('grant-applications:previous-applications', args=(self.gal.pk,))
        )

    def test_post_form_redirect_template(self, *mocks):
        response = self.client.post(
            self.url,
            {'duns_number': FAKE_GRANT_APPLICATION['company']['duns_number']},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, PreviousApplicationsView.template_name)

    def test_post_creates_backoffice_company(self, m_search_companies, m_update_grant_application,
                                             m_list_companies, m_get_grant_application,
                                             m_create_company):
        # mock out that list_companies returns nothing
        # so that create_company gets called to create the company
        m_list_companies.return_value = []

        response = self.client.post(
            self.url, data={'duns_number': FAKE_GRANT_APPLICATION['company']['duns_number']}
        )
        self.assertEqual(response.status_code, 302)
        m_create_company.assert_called_once_with(
            duns_number=str(FAKE_GRANT_APPLICATION['company']['duns_number']),
            registration_number=FAKE_GRANT_APPLICATION['company']['registration_number'],
            name=FAKE_GRANT_APPLICATION['company']['name']
        )

    def test_post_list_companies_finds_too_many_backoffice_companies(self, m_search_companies,
                                                                     m_update_grant_application,
                                                                     m_list_companies,
                                                                     m_get_grant_application,
                                                                     m_create_company):
        # mock out that list_companies returns more than 1 companies
        m_list_companies.return_value = [FAKE_COMPANY, FAKE_COMPANY]

        response = self.client.post(
            self.url, data={'duns_number': FAKE_GRANT_APPLICATION['company']['duns_number']}
        )

        # This means there is a problem in the backoffice api
        self.assertFormError(response, 'form', None, self.form_msgs['resubmit'])

        m_create_company.assert_not_called()
        self.log_capture.check_present(
            ('web.grant_applications.services', 'ERROR', 'Too many companies'),
        )

    def test_post_list_companies_causes_backoffice_service_exception(self, *mocks):
        mocks[2].side_effect = [BackofficeServiceException]
        response = self.client.post(
            self.url,
            data={'duns_number': FAKE_GRANT_APPLICATION['company']['duns_number']},
            follow=True
        )
        self.assertFormError(response, 'form', None, self.form_msgs['resubmit'])

    def test_post_updates_backoffice_grant_application_company(self, m_search_companies,
                                                               m_update_grant_application,
                                                               m_list_companies,
                                                               m_get_grant_application,
                                                               m_create_company):
        response = self.client.post(
            self.url, data={'duns_number': FAKE_GRANT_APPLICATION['company']['duns_number']}
        )
        self.assertEqual(response.status_code, 302)
        m_update_grant_application.assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            company=FAKE_COMPANY['id'],
            # Set manual company details to None in case they have previously been set
            is_based_in_uk=None,
            number_of_employees=None,
            is_turnover_greater_than=None
        )


@patch.object(BackofficeService, 'create_company', return_value=FAKE_COMPANY)
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestBusinessDetailsView(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:business-details', args=(self.gal.pk,))

    def test_get_template(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, BusinessDetailsView.template_name)

    def test_post(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'is_based_in_uk': True,
                'number_of_employees': BusinessDetailsForm.NumberOfEmployees.HAS_FEWER_THAN_10,
                'is_turnover_greater_than': True
            })
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            is_based_in_uk=True,
            number_of_employees=BusinessDetailsForm.NumberOfEmployees.HAS_FEWER_THAN_10.value,
            is_turnover_greater_than=True,
            # company is automatically set to None in case it has been set previously
            company=None
        )

    def test_post_cannot_set_company_field(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'is_based_in_uk': True,
                'number_of_employees': BusinessDetailsForm.NumberOfEmployees.HAS_FEWER_THAN_10,
                'is_turnover_greater_than': True,
                'company': FAKE_COMPANY['id']
            })
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            is_based_in_uk=True,
            number_of_employees=BusinessDetailsForm.NumberOfEmployees.HAS_FEWER_THAN_10.value,
            is_turnover_greater_than=True,
            # There is a hidden company field which sets the company as None
            # in case it has been set previously
            company=None
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
        response = self.client.post(self.url, content_type='application/x-www-form-urlencoded')
        self.assertFormError(response, 'form', 'is_based_in_uk', self.form_msgs['required'])
        self.assertFormError(response, 'form', 'number_of_employees', self.form_msgs['required'])
        self.assertFormError(
            response, 'form', 'is_turnover_greater_than', self.form_msgs['required']
        )


@patch.object(BackofficeService, 'search_companies', return_value=FAKE_SEARCH_COMPANIES)
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestPreviousApplicationsView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:previous-applications', kwargs={'pk': self.gal.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, PreviousApplicationsView.template_name)

    def test_default_back_url_when_no_referer_set(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        back_html = BeautifulSoup(response.content, 'html.parser').find(id='id_back_link')
        self.assertEqual(
            back_html.attrs['href'],
            reverse('grant-applications:select-company', args=(self.gal.pk,))
        )

    def test_back_url_is_select_company(self, *mocks):
        response = self.client.get(
            self.url,
            HTTP_REFERER=reverse('grant-applications:select-company', args=(self.gal.pk,))
        )
        self.assertEqual(response.status_code, 200)
        back_html = BeautifulSoup(response.content, 'html.parser').find(id='id_back_link')
        self.assertEqual(
            back_html.attrs['href'],
            reverse('grant-applications:select-company', args=(self.gal.pk,))
        )

    def test_back_url_is_business_details(self, *mocks):
        response = self.client.get(
            self.url,
            HTTP_REFERER=reverse('grant-applications:business-details', args=(self.gal.pk,))
        )
        self.assertEqual(response.status_code, 200)
        back_html = BeautifulSoup(response.content, 'html.parser').find(id='id_back_link')
        self.assertEqual(
            back_html.attrs['href'],
            reverse('grant-applications:business-details', args=(self.gal.pk,))
        )

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

    def test_true_for_has_previously_applied_makes_previous_applications_None(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({'has_previously_applied': True})
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            has_previously_applied=True,
            previous_applications=None
        )

    def test_null_out_previous_applications_when_has_previously_applied_true(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'has_previously_applied': True,
                'previous_applications': 2
            })
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            has_previously_applied=True,
            previous_applications=None
        )

    def test_false_for_has_previously_applied_makes_previous_applications_required(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({'has_previously_applied': False})
        )
        self.assertFormError(response, 'form', 'previous_applications', self.form_msgs['required'])
        mocks[0].assert_not_called()

    def test_boolean_field_must_be_present(self, *mocks):
        response = self.client.post(self.url, content_type='application/x-www-form-urlencoded')
        self.assertFormError(response, 'form', 'has_previously_applied', self.form_msgs['required'])


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'list_trade_events', return_value=[FAKE_EVENT])
class TestAboutTheEventView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:about-the-event', args=(self.gal.pk,))

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AboutTheEventView.template_name)

    def test_initial_filters_are_set_to_all(self, *mocks):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)
        if response.context_data['feature_flags']['filters']:
            # Filter by start date
            self.assertEqual(
                soup.find(id='id_filter_by_start_date').find('option', selected=True).text, 'All'
            )
            # Filter by country
            self.assertEqual(
                soup.find(id='id_filter_by_country').find('option', selected=True).text, 'All'
            )
            # Filter by sector
            self.assertEqual(
                soup.find(id='id_filter_by_sector').find('option', selected=True).text, 'All'
            )

    def test_event_initial_is_backoffice_event_when_filters_set_to_all(self, *mocks):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        selected_event = soup.find(id='id_event').find('option', selected=True)
        self.assertEqual(response.status_code, 200)
        self.assertInHTML(selected_event.attrs['value'], FAKE_EVENT['id'])
        self.assertInHTML(selected_event.text, FAKE_EVENT['display_name'])

    @patch.object(BackofficeService, 'get_grant_application')
    def test_initial_when_no_event_set(self, *mocks):
        mocks[3].return_value = FAKE_GRANT_APPLICATION.copy()
        mocks[3].return_value['event'] = None
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        selected_event = soup.find(id='id_event').find('option', selected=True)
        self.assertEqual(response.status_code, 200)
        self.assertInHTML(selected_event.attrs['value'], '')
        self.assertInHTML(selected_event.text, 'Select...')

    def test_post_redirects(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'event': FAKE_EVENT['id'],
                'form_button': ''
            })
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response=response,
            expected_url=reverse(AboutTheEventView.success_url_name, args=(self.gal.pk,))
        )

    def test_event_is_saved_on_form_continue_button(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'event': FAKE_EVENT['id'],
                'form_button': ''
            })
        )
        self.assertEqual(response.status_code, 302)
        mocks[1].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            event=FAKE_EVENT['id']
        )

    def test_filter_by_start_date(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'apply_filter_button': '',
                'filter_by_start_date': '2020-12-04',
            })
        )
        self.assertEqual(response.status_code, 200)
        mocks[0].assert_any_call(params={'start_date': '2020-12-04'})

    def test_filter_by_country(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'apply_filter_button': '',
                'filter_by_country': 'Country 1',
            })
        )
        self.assertEqual(response.status_code, 200)
        mocks[0].assert_any_call(params={'country': 'Country 1'})

    def test_filter_by_sector(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'apply_filter_button': '',
                'filter_by_sector': 'Sector 1',
            })
        )
        self.assertEqual(response.status_code, 200)
        mocks[0].assert_any_call(params={'sector': 'Sector 1'})

    def test_form_error_on_post_when_no_button_name_provided(self, *mocks):
        response = self.client.post(self.url, content_type='application/x-www-form-urlencoded')
        self.assertFormError(response, 'form', None, 'Form button name required.')

    def test_event_required_on_form_button_submit(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({'form_button': ''})
        )
        self.assertFormError(response, 'form', 'event', self.form_msgs['required'])

    def test_event_not_required_on_apply_filter_button_submit(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({'apply_filters_button': ''})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AboutTheEventView.template_name)
        self.assertFalse(response.context_data['form'].errors)

    def test_event_not_required_on_clear_filter_button_submit(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({'clear_filters_button': ''})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AboutTheEventView.template_name)
        self.assertFalse(response.context_data['form'].errors)


@patch.object(
    BackofficeService, 'get_grant_application',
    side_effect=[
        FAKE_GRANT_APPLICATION, FAKE_GRANT_APPLICATION, FAKE_FLATTENED_GRANT_APPLICATION,
        FAKE_FLATTENED_GRANT_APPLICATION
    ]
)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestEventFinanceView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:event-finance', args=(self.gal.pk,))

    def test_get_template(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, EventFinanceView.template_name)

    def test_form_details(self, *mocks):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(soup.find_all('details')), 3)

    def test_post_redirects(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'is_already_committed_to_event': True,
                'is_intending_on_other_financial_support': True,
                'has_received_de_minimis_aid': False,
            })
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response=response,
            expected_url=reverse(EventFinanceView.success_url_name, args=(self.gal.pk,))
        )

    def test_post_data_is_saved(self, *mocks):
        self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'is_already_committed_to_event': True,
                'is_intending_on_other_financial_support': False,
                'has_received_de_minimis_aid': False,
            })
        )
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            is_already_committed_to_event=True,
            is_intending_on_other_financial_support=False,
            has_received_de_minimis_aid=False
        )

    def test_boolean_fields_must_be_present(self, *mocks):
        response = self.client.post(self.url, content_type='application/x-www-form-urlencoded')
        self.assertFormError(
            response, 'form', 'is_already_committed_to_event', self.form_msgs['required']
        )
        self.assertFormError(
            response, 'form', 'is_intending_on_other_financial_support', self.form_msgs['required']
        )
        self.assertFormError(
            response, 'form', 'has_received_de_minimis_aid', self.form_msgs['required']
        )


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
        self.client.post(self.url, content_type='application/x-www-form-urlencoded')
        mocks[1].assert_not_called()

    @patch.object(
        BackofficeService, 'get_grant_application',
        side_effect=[FAKE_GRANT_APPLICATION, FAKE_GRANT_APPLICATION]
    )
    def test_post_redirects(self, *mocks):
        response = self.client.post(self.url, content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            expected_url=reverse(EligibilityReviewView.success_url_name, args=(self.gal.pk,))
        )


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestEligibilityConfirmationView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:eligibility-confirmation', args=(self.gal.pk,))

    def test_get_template(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, EligibilityConfirmationView.template_name)

    def test_table_context(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('table', response.context_data)

    def test_post(self, *mocks):
        self.client.post(self.url, content_type='application/x-www-form-urlencoded')
        mocks[0].assert_not_called()

    def test_post_redirects(self, *mocks):
        response = self.client.post(self.url, content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            expected_url=reverse(EligibilityConfirmationView.success_url_name, args=(self.gal.pk,))
        )


@patch.object(BackofficeService, 'list_sectors', return_value=[FAKE_SECTOR])
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'list_trade_events', return_value=[FAKE_EVENT])
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestAboutYouView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:about-you', kwargs={'pk': self.gal.pk})

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
                'applicant_mobile_number': '+447777777777',
                'applicant_position_within_business': 'director'
            })
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response=response,
            expected_url=reverse(AboutYouView.success_url_name, kwargs={'pk': self.gal.pk})
        )

    def test_required_fields(self, *mocks):
        response = self.client.post(self.url, content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 200)
        msg = 'This field is required.'
        self.assertFormError(response, 'form', 'applicant_full_name', msg)
        self.assertFormError(response, 'form', 'applicant_email', msg)
        self.assertFormError(response, 'form', 'applicant_mobile_number', msg)
        self.assertFormError(response, 'form', 'applicant_position_within_business', msg)

    def test_post_data_is_saved(self, *mocks):
        self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'applicant_full_name': 'A Name',
                'applicant_email': 'test@test.com',
                'applicant_mobile_number': '07777777777',
                'applicant_position_within_business': 'director'
            })
        )
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            applicant_full_name='A Name',
            applicant_email='test@test.com',
            applicant_mobile_number='+447777777777',
            applicant_position_within_business='director'
        )

    def test_mobile_must_be_gb_number_international(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({'applicant_mobile_number': '+457777777777'})
        )
        self.assertFormError(
            response, 'form', 'applicant_mobile_number',
            "Enter a valid phone number (e.g. 0121 234 5678) or a number with an international "
            "call prefix."
        )

    def test_mobile_must_be_gb_number_national(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({'applicant_mobile_number': '2025550154'})
        )
        self.assertFormError(
            response, 'form', 'applicant_mobile_number',
            "Enter a valid phone number (e.g. 0121 234 5678) or a number with an international "
            "call prefix."
        )


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'list_sectors', return_value=[FAKE_SECTOR])
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestBusinessInformationView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:business-information', kwargs={'pk': self.gal.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, BusinessInformationView.template_name)

    def test_sector_choices_come_from_sector_model(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        options = soup.find_all('option')
        self.assertEqual(options[1].text, FAKE_SECTOR['full_name'])

    def test_post(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'goods_and_services_description': 'A description',
                'other_business_names': 'A name',
                'sector': FAKE_SECTOR['id'],
            })
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            goods_and_services_description='A description',
            other_business_names='A name',
            sector=FAKE_SECTOR['id'],
        )

    def test_other_business_names_not_required(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'goods_and_services_description': 'A description',
                'sector': FAKE_SECTOR['id'],
            })
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            goods_and_services_description='A description',
            other_business_names=None,
            sector=FAKE_SECTOR['id'],
        )

    def test_initial_form_data_from_grant_application_object(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(
            soup.find('textarea', attrs={'name': 'goods_and_services_description'}).text,
            FAKE_GRANT_APPLICATION['goods_and_services_description']
        )
        self.assertInHTML(
            soup.find('input', attrs={'name': 'other_business_names'}).attrs['value'],
            FAKE_GRANT_APPLICATION['other_business_names']
        )
        self.assertEqual(
            soup.find(id='id_sector').find('option', selected=True).attrs['value'],
            FAKE_GRANT_APPLICATION['sector']['id']
        )

    def test_redirect_to_confirmation_page_if_application_already_sent_for_review(self, *mocks):
        self.gal.sent_for_review = True
        self.gal.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(
    BackofficeService, 'list_sectors',
    return_value=[{'id': 1, 'full_name': 'full-name-1'}, {'id': 2, 'full_name': 'full-name-2'}]
)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestEventIntentionView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:event-intention', kwargs={'pk': self.gal.pk})

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

    def test_true_is_first_exhibit_at_event_makes_number_of_times_exhibited_optional(self, *mocks):
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
            number_of_times_exhibited_at_event=None
        )

    def test_false_is_first_exhibit_at_event_makes_number_of_times_exhibited_required(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({'is_first_exhibit_at_event': False})
        )
        self.assertFormError(
            response, 'form', 'number_of_times_exhibited_at_event', self.form_msgs['required']
        )
        mocks[0].assert_not_called()


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
        self.url = reverse('grant-applications:state-aid', kwargs={'pk': self.gal.pk})

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
            has_received_de_minimis_aid=False,
            de_minimis_aid_public_authority=None,
            de_minimis_aid_date_awarded=None,
            de_minimis_aid_amount=None,
            de_minimis_aid_description=None,
            de_minimis_aid_recipient=None,
            de_minimis_aid_date_received=None
        )

    def test_required_fields_when_aid_is_selected(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({'has_received_de_minimis_aid': True})
        )
        self.assertEqual(response.status_code, 200)
        msg = self.form_msgs['required']
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
        response = self.client.post(self.url, content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 302)
        redirect = resolve(response.url)
        self.assertEqual(redirect.kwargs['pk'], str(self.gal.id))
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )

    def test_sent_for_review(self, *mocks):
        self.client.get(self.url)
        self.client.post(self.url, content_type='application/x-www-form-urlencoded')
        self.gal.refresh_from_db()
        self.assertTrue(self.gal.sent_for_review)
        self.assertIn('application_summary', self.client.session)
        mocks[3].assert_called_once_with(
            str(self.gal.backoffice_grant_application_id),
            application_summary=self.client.session['application_summary']
        )

    def test_sent_for_review_not_set_on_backoffice_error(self, *mocks):
        mocks[3].side_effect = [BackofficeServiceException]
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
