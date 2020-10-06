from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView, TemplateView

from web.core.view_mixins import PageContextMixin, SuccessUrlObjectPkMixin, BackContextMixin
from web.grant_applications.forms import (
    SearchCompanyForm, SelectCompanyForm, AboutYouForm, AboutTheEventForm, PreviousApplicationsForm,
    EventIntentionForm, BusinessInformationForm, ExportExperienceForm, StateAidForm,
    ApplicationReviewForm, EligibilityReviewForm, EventFinanceForm, EligibilityConfirmationForm
)
from web.grant_applications.models import GrantApplicationLink
from web.grant_applications.services import (
    generate_grant_application_summary, BackofficeServiceException
)
from web.grant_applications.view_mixins import (
    BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin
)


class SearchCompanyView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin, CreateView):
    form_class = SearchCompanyForm
    template_name = 'grant_applications/search_company.html'
    back_url_name = 'grant-applications:index'
    success_url_name = 'grant-applications:select-company'
    page = {
        'heading': _('Search for your company')
    }


class SelectCompanyView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                        BackofficeMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = SelectCompanyForm
    template_name = 'grant_applications/select_company.html'
    success_url_name = 'grant-applications:previous-applications'
    page = {
        'heading': _('Select your company')
    }

    @staticmethod
    def get_back_url():
        return reverse('grant-applications:search-company')

    def get_initial(self):
        initial = super().get_initial()
        if hasattr(self, 'backoffice_grant_application'):
            initial['duns_number'] = self.backoffice_grant_application['company']['duns_number']
        return initial


class PreviousApplicationsView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                               BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin,
                               UpdateView):
    model = GrantApplicationLink
    form_class = PreviousApplicationsForm
    template_name = 'grant_applications/previous_applications.html'
    back_url_name = 'grant-applications:select-company'
    success_url_name = 'grant_applications:about-the-event'
    page = {
        'heading': _('Previous TAP grants')
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            if kwargs['data'].get('has_previously_applied') == 'True':
                kwargs['data'] = {
                    'has_previously_applied': True,
                    'previous_applications': 0
                }
        return kwargs


class AboutTheEventView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                        BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = AboutTheEventForm
    template_name = 'grant_applications/about_the_event.html'
    back_url_name = 'grant-applications:previous-applications'
    success_url_name = 'grant_applications:event-finance'
    page = {
        'heading': _('Select an event'),
    }

    def get_initial(self):
        initial = super().get_initial()
        if self.backoffice_grant_application['event']:
            initial['event'] = self.backoffice_grant_application['event']['id']
        return initial

    def _get_form_button_name(self):
        has_form_button_name = [i for i in self.request.POST if '_button' in i]
        if has_form_button_name:
            return has_form_button_name[0]

    def get_form(self, form_class=None):
        if self.request.method == 'GET':
            return super().get_form(form_class)

        if form_class is None:
            form_class = self.get_form_class()

        form_kwargs = self.get_form_kwargs()

        if self.form_button_name == 'form_button':
            return form_class(**form_kwargs)
        elif self.form_button_name == 'apply_filters_button':
            form_kwargs['initial'] = {}
            form_kwargs['data'] = form_kwargs['data'].copy()
            form_kwargs['data'].pop('event', None)
            return form_class(**form_kwargs)
        elif self.form_button_name == 'clear_filters_button':
            form_kwargs['data'] = {}
            return form_class(**form_kwargs)

        form = super().get_form(form_class)
        form.add_error(None, forms.ValidationError('Form button name required.'))
        return form

    def form_valid(self, form):
        if self.form_button_name == 'form_button':
            # If button name is "form_button" then we submit the form and redirect
            return super().form_valid(form)
        elif self.form_button_name in ['apply_filters_button', 'clear_filters_button']:
            # If button name is "*_filter_button" then we apply filters and redisplay the form
            return self.render_to_response(self.get_context_data(form=form))

        # If no form button was clicked (in a POST/PUT request) then something has gone wrong
        raise forms.ValidationError('Form button name required.')

    def post(self, request, *args, **kwargs):
        self.form_button_name = self._get_form_button_name()
        return super(AboutTheEventView, self).post(request, *args, **kwargs)


class EventFinanceView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                       BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = EventFinanceForm
    template_name = 'grant_applications/event_finance.html'
    back_url_name = 'grant-applications:about-the-event'
    success_url_name = 'grant_applications:eligibility-review'
    page = {
        'heading': _('Event finance')
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'].format_label(
            field_name='is_already_committed_to_event',
            event_name=self.backoffice_grant_application['event']['name']
        )
        return context


class EligibilityReviewView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                            InitialDataMixin, BackofficeMixin, ConfirmationRedirectMixin,
                            UpdateView):
    model = GrantApplicationLink
    form_class = EligibilityReviewForm
    template_name = 'grant_applications/eligibility_review.html'
    back_url_name = 'grant-applications:event-finance'
    success_url_name = 'grant_applications:eligibility-confirmation'
    page = {
        'heading': _('Confirm your answers'),
        'form_button_text': _('Confirm')
    }

    def company_summary_list(self):
        dnb = self.backoffice_grant_application['company']['last_dnb_get_company_response']
        return {
            'heading': _('Your company details'),
            'summary': [
                {
                    'key': _('Company'),
                    'value': '\n'.join([
                        self.backoffice_grant_application['company']['name'],
                        dnb['company_registration_number'],
                        dnb['company_address'],
                    ]),
                    'action': {
                        'url': reverse('grant-applications:search-company')
                    }
                }
            ]
        }

    def previous_apps_summary_list(self):
        summary = generate_grant_application_summary(
            form_class=PreviousApplicationsView.form_class,
            grant_application=self.object,
            url=reverse('grant-applications:previous-applications', args=(self.object.pk,))
        )
        return {
            'heading': _('Previous TAP grants'),
            'summary': summary
        }

    def event_summary_list(self):
        return {
            'heading': _('Event details'),
            'summary': [
                {
                    'key': _('Event'),
                    'value': '\n'.join([
                        self.backoffice_grant_application['event']['name'],
                        self.backoffice_grant_application['event']['sector'],
                        f"{self.backoffice_grant_application['event']['start_date']} to "
                        f"{self.backoffice_grant_application['event']['end_date']}"
                    ]),
                    'action': {
                        'url': reverse('grant-applications:about-the-event', args=(self.object.pk,))
                    }
                }
            ]
        }

    def event_finance_summary_list(self):
        summary = generate_grant_application_summary(
            form_class=EventFinanceView.form_class,
            grant_application=self.object,
            url=reverse('grant-applications:event-finance', args=(self.object.pk,))
        )
        return {
            'heading': _('Event finance'),
            'summary': summary
        }

    def get_context_data(self, **kwargs):
        kwargs['summary_lists'] = [
            self.company_summary_list(),
            self.previous_apps_summary_list(),
            self.event_summary_list(),
            self.event_finance_summary_list()
        ]
        return super().get_context_data(**kwargs)


class EligibilityConfirmationView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                                  InitialDataMixin, BackofficeMixin, ConfirmationRedirectMixin,
                                  UpdateView):
    model = GrantApplicationLink
    form_class = EligibilityConfirmationForm
    template_name = 'grant_applications/eligibility_confirmation.html'
    success_url_name = 'grant_applications:about-you'
    page = {
        'heading': _('You are eligible for a TAP grant'),
        'form_button_text': _('Apply for a grant')
    }

    def get_context_data(self, **kwargs):
        kwargs['table'] = {
            'rows': [{
                'label': f"Grant available for "
                         f"{self.backoffice_grant_application['event']['name']}",
                'value': '£1500',  # TODO: get event grant value from event data
            }]
        }
        return super().get_context_data(**kwargs)


class AboutYouView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin, BackofficeMixin,
                   InitialDataMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = AboutYouForm
    template_name = 'grant_applications/generic_form_page.html'
    back_url_name = 'grant-applications:about-the-event'
    success_url_name = 'grant_applications:about-you'  # TODO: End user journey here for now
    page = {
        'heading': _('About you')
    }


class EventIntentionView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                         BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = EventIntentionForm
    template_name = 'grant_applications/event_intention.html'
    back_url_name = 'grant-applications:about-you'
    success_url_name = 'grant_applications:business-information'
    page = {
        'heading': _('Your application')
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'].format_label(
            field_name='is_first_exhibit_at_event',
            event_name=self.backoffice_grant_application['event']['name']
        )
        context['form'].format_label(
            field_name='number_of_times_exhibited_at_event',
            event_name=self.backoffice_grant_application['event']['name']
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            if kwargs['data'].get('is_first_exhibit_at_event') == 'True':
                kwargs['data'] = {
                    'is_first_exhibit_at_event': True,
                    'number_of_times_exhibited_at_event': 0
                }
        return kwargs


class BusinessInformationView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                              BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin,
                              UpdateView):
    model = GrantApplicationLink
    form_class = BusinessInformationForm
    template_name = 'grant_applications/generic_form_page.html'
    back_url_name = 'grant-applications:event-intention'
    success_url_name = 'grant_applications:export-experience'
    page = {
        'heading': _('About your business')
    }

    def get_initial(self):
        initial = super().get_initial()
        company_data = self.backoffice_grant_application['company']

        if not self.backoffice_grant_application['business_name_at_exhibit']:
            initial['business_name_at_exhibit'] = company_data['name']

        if not self.backoffice_grant_application['turnover']:
            initial['turnover'] = int(
                company_data['last_dnb_get_company_response']['data']['annual_sales']
            )

        if not self.backoffice_grant_application['number_of_employees']:
            initial['number_of_employees'] = self.form_class.NumberOfEmployees.get_choice_by_number(
                company_data['last_dnb_get_company_response']['data']['employee_number']
            )

        if not self.backoffice_grant_application['website']:
            initial['website'] = company_data['last_dnb_get_company_response']['data']['domain']

        return initial


class ExportExperienceView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                           BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin,
                           UpdateView):
    model = GrantApplicationLink
    form_class = ExportExperienceForm
    template_name = 'grant_applications/generic_form_page.html'
    back_url_name = 'grant-applications:business-information'
    success_url_name = 'grant_applications:state-aid'
    page = {
        'heading': _('About your export experience')
    }


class StateAidView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin, BackofficeMixin,
                   InitialDataMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = StateAidForm
    template_name = 'grant_applications/state_aid.html'
    back_url_name = 'grant-applications:export-experience'
    success_url_name = 'grant_applications:application-review'
    page = {
        'heading': _('State aid restrictions')
    }


class ApplicationReviewView(BackContextMixin, PageContextMixin, SuccessUrlObjectPkMixin,
                            BackofficeMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = ApplicationReviewForm
    template_name = 'grant_applications/application_review.html'
    back_url_name = 'grant-applications:state-aid'
    success_url_name = 'grant_applications:confirmation'
    page = {
        'heading': _('Review your application'),
        'form_button_text': _('Accept and send'),
    }
    grant_application_flow = [
        SelectCompanyView,
        AboutYouView,
        AboutTheEventView,
        PreviousApplicationsView,
        EventIntentionView,
        BusinessInformationView,
        ExportExperienceView,
        StateAidView,
    ]

    def generate_application_summary(self):
        application_summary = []

        url = SearchCompanyView(object=self.object).get_success_url()

        for view_class in self.grant_application_flow:
            summary = generate_grant_application_summary(
                form_class=view_class.form_class, grant_application=self.object, url=url
            )
            if summary:
                application_summary.append({
                    'heading': str(view_class.page.get('heading', '')),
                    'summary': summary
                })
            url = view_class(object=self.object).get_success_url()

        return application_summary

    def get_context_data(self, **kwargs):
        kwargs['application_summary'] = self.generate_application_summary()
        self.request.session['application_summary'] = kwargs['application_summary']
        return super().get_context_data(**kwargs)

    def try_send_grant_application_for_review(self, form):
        try:
            self.backoffice_service.send_grant_application_for_review(
                str(self.object.backoffice_grant_application_id),
                application_summary=self.request.session['application_summary']
            )
        except BackofficeServiceException:
            msg = forms.ValidationError('An unexpected error occurred. Please resubmit the form.')
            form.add_error(None, msg)
        else:
            self.object.sent_for_review = True

        return form

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        self.try_send_grant_application_for_review(form)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ConfirmationView(PageContextMixin, TemplateView):
    template_name = 'grant_applications/confirmation.html'
    page = {
        'panel_title': _('Application complete'),
        'panel_ref_text': _('Your reference number'),
        'confirmation_email_text': _('We have sent you a confirmation email.'),
        'next_steps_heading': _('What happens next'),
        'next_steps_line_1': _("We've sent your application to the Trade Access Program team."),
        'next_steps_line_2': _('They will contact you either to confirm your registration, or '
                               'to ask for more information.'),
    }
