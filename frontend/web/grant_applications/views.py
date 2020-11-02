from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse, resolve
from django.utils import timezone
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView, TemplateView, RedirectView
from django.views.generic.detail import SingleObjectMixin

from web.core.forms import FORM_MSGS
from web.core.view_mixins import (
    StaticContextMixin, SuccessUrlObjectPkMixin, BackContextMixin, PaginationMixin
)
from web.grant_applications.forms import (
    SearchCompanyForm, SelectCompanyForm, SelectAnEventForm, PreviousApplicationsForm,
    CompanyTradingDetailsForm, ExportExperienceForm, FindAnEventForm,
    EmptyGrantApplicationLinkForm, EventCommitmentForm, CompanyDetailsForm, ContactDetailsForm,
    ExportDetailsForm, TradeEventDetailsForm, AddStateAidForm, EditStateAidForm
)
from web.grant_applications.models import GrantApplicationLink
from web.grant_applications.services import (
    generate_grant_application_summary, BackofficeServiceException, BackofficeService,
    get_companies_from_search_term, get_state_aid_summary_table
)
from web.grant_applications.view_mixins import (
    BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin
)


class BeforeYouStartView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin, CreateView):
    model = GrantApplicationLink
    form_class = EmptyGrantApplicationLinkForm
    template_name = 'grant_applications/before_you_start.html'
    back_url_name = 'grant-applications:index'
    success_url_name = 'grant_applications:previous-applications'
    static_context = {
        'page': {
            'heading': _('What you will need')
        }
    }

    def form_valid(self, form):
        try:
            backoffice_grant_application = BackofficeService().create_grant_application()
        except BackofficeServiceException:
            form.add_error(None, forms.ValidationError(FORM_MSGS['resubmit']))
            return super().form_invalid(form)
        form.instance.backoffice_grant_application_id = backoffice_grant_application['id']
        return super().form_valid(form)


class PreviousApplicationsView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
                               BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin,
                               UpdateView):
    model = GrantApplicationLink
    form_class = PreviousApplicationsForm
    template_name = 'grant_applications/previous_applications.html'
    back_url_name = 'grant-applications:before-you-start'
    success_url_name = 'grant_applications:find-an-event'
    static_context = {
        'page': {
            'heading':  _('Previous TAP grants')
        }
    }

    def get_back_url(self):
        return reverse(self.back_url_name)


class FindAnEventView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
                      BackofficeMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = FindAnEventForm
    template_name = 'grant_applications/find_an_event.html'
    back_url_name = 'grant-applications:previous-applications'
    success_url_name = 'grant_applications:select-an-event'
    static_context = {
        'page': {
            'heading':  _('Find an event')
        }
    }

    def get_success_url(self, **params):
        if hasattr(self, 'request'):
            params = {
                'filter_by_name': self.request.POST['filter_by_name'],
                'filter_by_sector': self.request.POST['filter_by_sector'],
                'filter_by_country': self.request.POST['filter_by_country'],
                'filter_by_month': self.request.POST['filter_by_month'],
            }
        return super().get_success_url() + f'?{urlencode(params)}'

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        trade_event_aggregates = self.backoffice_service.get_trade_event_aggregates(
            start_date_from=timezone.now().date()
        )
        kwargs.update({
            'total_trade_events': trade_event_aggregates['total_trade_events'],
            'trade_event_total_months': len(trade_event_aggregates['trade_event_months']),
        })
        return kwargs


class SelectAnEventView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
                        BackofficeMixin, ConfirmationRedirectMixin, PaginationMixin, UpdateView):
    model = GrantApplicationLink
    form_class = SelectAnEventForm
    template_name = 'grant_applications/select_an_event.html'
    back_url_name = 'grant-applications:find-an-event'
    success_url_name = 'grant_applications:event-commitment'
    static_context = {
        'page': {
            'heading':  _('Select an event')
        },
        'button_text': 'Select and continue',
    }
    events_page_size = 10
    grant_application_fields = ['event']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['trade_events'] = self.trade_events
        kwargs['initial'].update({
            'filter_by_name': self.request.GET.get('filter_by_name'),
            'filter_by_country': self.request.GET.get('filter_by_country'),
            'filter_by_sector': self.request.GET.get('filter_by_sector'),
            'filter_by_month': self.request.GET.get('filter_by_month'),
        })
        return kwargs

    def get_pagination_total_pages(self):
        if self.trade_events:
            return self.trade_events['total_pages']

    def get_extra_pagination_href_params(self):
        params = self.request.GET.copy()
        params.pop('page', None)
        return params.dict()

    def get_trade_events(self):
        params = {
            'search': self.request.GET.get('filter_by_name'),
            'country': self.request.GET.get('filter_by_country'),
            'sector': self.request.GET.get('filter_by_sector')
        }
        filter_by_month = self.request.GET.get('filter_by_month')
        if filter_by_month:
            params['start_date_range_after'] = filter_by_month.split(':')[0]
            params['end_date_range_before'] = filter_by_month.split(':')[1]

        try:
            trade_events = BackofficeService().list_trade_events(
                page=self.get_current_page(),
                page_size=self.events_page_size,
                **{k: v for k, v in params.items() if v}
            )
        except BackofficeServiceException:
            trade_events = None

        return trade_events

    def get_context_data(self, **kwargs):
        if self.trade_events:
            kwargs['number_of_events'] = self.trade_events['count']
            kwargs['results_to'] = self.get_current_page() * self.events_page_size
            kwargs['results_from'] = kwargs['results_to'] - self.events_page_size + 1
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.trade_events = self.get_trade_events()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.trade_events = self.get_trade_events()
        return super().post(request, *args, **kwargs)


class EventCommitmentView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
                          BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = EventCommitmentForm
    template_name = 'grant_applications/event_commitment.html'
    back_url_name = 'grant-applications:select-an-event'
    success_url_name = 'grant_applications:search-company'
    static_context = {
        'page': {
            'heading': _('Event commitment')
        }
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'].format_label(
            field_name='is_already_committed_to_event',
            event_name=self.backoffice_grant_application['event']['name']
        )
        return context


class SearchCompanyView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
                        BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = SearchCompanyForm
    template_name = 'grant_applications/search_company.html'
    back_url_name = 'grant-applications:event-commitment'
    success_url_name = 'grant-applications:select-company'
    static_context = {
        'page': {
            'heading': _('Find your business')
        },
        'button_text': 'Search'
    }

    def get_success_url(self):
        query = ''
        if hasattr(self, 'request'):
            query = f"?search_term={self.request.POST['search_term']}"
        return super().get_success_url() + query


class SelectCompanyView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
                        BackofficeMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = SelectCompanyForm
    template_name = 'grant_applications/select_company.html'
    back_url_name = 'grant-applications:search-company'
    success_url_name = 'grant-applications:company-details'
    static_context = {
        'page': {
            'heading':  _('Find your business')
        },
        'button_text': 'Select and continue'
    }
    grant_application_fields = ['company']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['companies'] = self.companies or get_companies_from_search_term(self.search_term)
        if self.request.method in ('POST', 'PUT'):
            kwargs['data'] = kwargs['data'].copy()
            kwargs['data']['search_term'] = self.request.GET.get('search_term')

        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial['search_term'] = self.request.GET.get('search_term')
        if hasattr(self, 'backoffice_grant_application') \
                and self.backoffice_grant_application['company']:
            initial['duns_number'] = self.backoffice_grant_application['company']['duns_number']
        return initial

    def form_valid(self, form):
        return super().form_valid(
            form,
            # Set manual company details to None in case they have previously been set
            # TODO: do we need this
            extra_grant_application_data={
                'is_based_in_uk': None,
                'number_of_employees': None,
                'is_turnover_greater_than': None,
            }
        )

    def get(self, request, *args, **kwargs):
        self.search_term = request.GET.get('search_term')
        if not self.search_term:
            return HttpResponseRedirect(
                reverse(self.back_url_name, args=(self.get_object().pk,))
            )
        self.companies = get_companies_from_search_term(self.search_term)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.search_term = request.GET.get('search_term')
        self.companies = BackofficeService().request_factory(
            'search_companies',
            raise_exception=False,
            duns_number=self.request.POST.get('duns_number')
        )
        return super().post(request, *args, **kwargs)


# TODO
# class ManualCompanyDetailsView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
#                                BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin,
#                                UpdateView):
#     model = GrantApplicationLink
#     form_class = CompanyDetailsForm
#     template_name = 'grant_applications/company_details.html'
#     back_url_name = 'grant-applications:select-company'
#     success_url_name = 'grant-applications:company-details'
#     static_context = {
#         'page': {
#             'heading':  _('Business details')
#         }
#     }
#
#     def form_valid(self, form):
#         # Set company to None in case it has been set previously
#         return super().form_valid(form, extra_grant_application_data={'company': None})


class CompanyDetailsView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
                         BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = CompanyDetailsForm
    template_name = 'grant_applications/company_details.html'
    back_url_name = 'grant-applications:select-company'
    success_url_name = 'grant-applications:contact-details'
    static_context = {
        'page': {
            'heading':  _('Business size and turnover')
        }
    }


class ContactDetailsView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
                         BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = ContactDetailsForm
    template_name = 'grant_applications/contact_details.html'
    back_url_name = 'grant-applications:company-details'
    success_url_name = 'grant_applications:company-trading-details'
    static_context = {
        'page': {
            'heading':  _('Business contact details')
        }
    }


class CompanyTradingDetailsView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
                                BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin,
                                UpdateView):
    model = GrantApplicationLink
    form_class = CompanyTradingDetailsForm
    template_name = 'grant_applications/company_trading_details.html'
    back_url_name = 'grant-applications:contact-details'
    success_url_name = 'grant_applications:export-experience'
    static_context = {
        'page': {
            'heading':  _('Business trading details')
        }
    }

    def get_initial(self):
        initial = super().get_initial()
        if self.backoffice_grant_application['sector']:
            initial['sector'] = self.backoffice_grant_application['sector']['id']
        return initial


class ExportExperienceView(BackContextMixin, StaticContextMixin, BackofficeMixin, InitialDataMixin,
                           ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = ExportExperienceForm
    template_name = 'grant_applications/export_experience.html'
    back_url_name = 'grant-applications:company-trading-details'
    static_context = {
        'page': {
            'heading':  _('Export experience')
        }
    }

    def get_success_url(self):
        if not hasattr(self, 'backoffice_grant_application'):
            self.backoffice_grant_application = BackofficeService().get_grant_application(
                self.object.backoffice_grant_application_id
            )
        if self.backoffice_grant_application['has_exported_before']:
            return reverse('grant-applications:export-details', args=(self.object.pk,))
        return reverse('grant-applications:trade-event-details', args=(self.object.pk,))


class ExportDetailsView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
                        BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = ExportDetailsForm
    template_name = 'grant_applications/export_details.html'
    back_url_name = 'grant-applications:export-experience'
    success_url_name = 'grant_applications:trade-event-details'
    static_context = {
        'page': {
            'heading':  _('Export details')
        }
    }


class TradeEventDetailsView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
                            BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin,
                            UpdateView):
    model = GrantApplicationLink
    form_class = TradeEventDetailsForm
    template_name = 'grant_applications/trade_event_details.html'
    success_url_name = 'grant_applications:state-aid-summary'
    static_context = {
        'page': {
            'heading':  _('Trade show experience')
        }
    }

    def get_back_url(self):
        if self.backoffice_grant_application['has_exported_before']:
            return reverse('grant-applications:export-details', args=(self.object.pk,))
        return reverse('grant-applications:export-experience', args=(self.object.pk,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'].format_label(
            field_name='interest_in_event_description',
            event_name=self.backoffice_grant_application['event']['name']
        )
        return context


class StateAidSummaryView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
                          BackofficeMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = EmptyGrantApplicationLinkForm
    template_name = 'grant_applications/state_aid_summary.html'
    back_url_name = 'grant-applications:export-experience'
    success_url_name = 'grant_applications:confirmation'
    static_context = {
        'page': {
            'heading':  _('State aid restrictions')
        }
    }

    def get_context_data(self, **kwargs):
        state_aid_items = self.backoffice_service.list_state_aids(
            grant_application=self.backoffice_grant_application['id']
        )
        kwargs['table'] = get_state_aid_summary_table(
            grant_application_link=self.object,
            state_aid_items=state_aid_items
        )
        return super().get_context_data(**kwargs)


class DeleteStateAidView(BackofficeMixin, SingleObjectMixin, RedirectView):
    model = GrantApplicationLink
    pattern_name = 'grant-applications:state-aid-summary'

    def get_redirect_url(self, *args, **kwargs):
        object = self.get_object()
        try:
            self.backoffice_service.delete_state_aid(state_aid_id=kwargs['state_aid_pk'])
        except BackofficeServiceException:
            pass
        return super().get_redirect_url(pk=object.pk)


class DuplicateStateAidView(BackofficeMixin, SingleObjectMixin, RedirectView):
    model = GrantApplicationLink
    pattern_name = 'grant-applications:state-aid-summary'

    def get_redirect_url(self, *args, **kwargs):
        object = self.get_object()
        try:
            state_aid = self.backoffice_service.get_state_aid(state_aid_id=kwargs['state_aid_pk'])
            self.backoffice_service.create_state_aid(
                grant_application=object.backoffice_grant_application_id,
                **{k: v for k, v in state_aid.items() if k in AddStateAidForm.Meta.fields}
            )
        except BackofficeServiceException:
            pass
        return super().get_redirect_url(pk=object.pk)


class StateAidItemMixin(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
                        BackofficeMixin, ConfirmationRedirectMixin):
    model = GrantApplicationLink
    template_name = 'grant_applications/state_aid_item.html'
    back_url_name = 'grant-applications:state-aid-summary'
    success_url_name = 'grant_applications:state-aid-summary'
    grant_application_fields = []


class AddStateAidView(StateAidItemMixin, UpdateView):
    form_class = AddStateAidForm
    static_context = {
        'page': {
            'heading': _('Add state aid')
        }
    }

    def form_valid(self, form):
        if form.cleaned_data:
            try:
                self.state_aid = self.backoffice_service.create_state_aid(
                    grant_application=str(form.instance.backoffice_grant_application_id),
                    **form.cleaned_data
                )
            except BackofficeServiceException:
                form.add_error(None, forms.ValidationError(FORM_MSGS['resubmit']))
                return super().form_invalid(form)
        return super().form_valid(form)


class EditStateAidView(StateAidItemMixin, UpdateView):
    form_class = EditStateAidForm
    static_context = {
        'page': {
            'heading': _('Edit state aid')
        }
    }

    def get_initial(self):
        state_aid = self.backoffice_service.get_state_aid(self.state_aid_id)
        return {
            'authority': state_aid['authority'],
            'amount': state_aid['amount'],
            'description': state_aid['description'],
            'date_received': state_aid['date_received'],
        }

    def form_valid(self, form):
        if form.cleaned_data:
            try:
                self.state_aid = self.backoffice_service.update_state_aid(
                        state_aid_id=self.state_aid_id,
                        **{k: v for k, v in form.cleaned_data.items() if v is not None}
                    )
            except BackofficeServiceException:
                form.add_error(None, forms.ValidationError(FORM_MSGS['resubmit']))
                return super().form_invalid(form)
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        self.state_aid_id = resolve(self.request.path).kwargs['state_aid_pk']
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.state_aid_id = resolve(self.request.path).kwargs['state_aid_pk']
        return super().post(request, *args, **kwargs)


class EligibilityReviewView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
                            InitialDataMixin, BackofficeMixin, ConfirmationRedirectMixin,
                            UpdateView):
    model = GrantApplicationLink
    form_class = EmptyGrantApplicationLinkForm
    template_name = 'grant_applications/eligibility_review.html'
    back_url_name = 'grant-applications:company-details'
    success_url_name = 'grant_applications:eligibility-confirmation'
    static_context = {
        'page': {
            'heading':  _('Confirm your answers')
        }
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
                        self.backoffice_grant_application['company']['registration_number'],
                        dnb['company_address'],
                    ]),
                    'action': {
                        'url': reverse('grant-applications:search-company', args=(self.object.pk,))
                    }
                }
            ]
        }

    def previous_apps_summary_list(self):
        summary = generate_grant_application_summary(
            grant_application=self.object,
            form_class=PreviousApplicationsView.form_class,
            form_kwargs={},
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
                        'url': reverse('grant-applications:select-an-event', args=(self.object.pk,))
                    }
                }
            ]
        }

    def get_context_data(self, **kwargs):
        kwargs['summary_lists'] = [
            self.company_summary_list(),
            self.previous_apps_summary_list(),
            self.event_summary_list(),
        ]
        return super().get_context_data(**kwargs)


class EligibilityConfirmationView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
                                  InitialDataMixin, BackofficeMixin, ConfirmationRedirectMixin,
                                  UpdateView):
    model = GrantApplicationLink
    form_class = EmptyGrantApplicationLinkForm
    template_name = 'grant_applications/eligibility_confirmation.html'
    success_url_name = 'grant_applications:contact-details'
    static_context = {
        'page': {
            'heading':  _('You are eligible for a TAP grant')
        }
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


class ApplicationReviewView(BackContextMixin, StaticContextMixin, SuccessUrlObjectPkMixin,
                            BackofficeMixin, ConfirmationRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = EmptyGrantApplicationLinkForm
    template_name = 'grant_applications/application_review.html'
    back_url_name = 'grant-applications:state-aid-summary'
    success_url_name = 'grant_applications:confirmation'
    static_context = {
        'page': {
            'heading':  _('Review your application')
        }
    }
    grant_application_flow = [
        # TODO: fix grant application review items
        {'view_class': PreviousApplicationsView},
        {'view_class': FindAnEventView},
        {'view_class': SelectAnEventView, 'form_kwargs': {'trade_events': None}},
        {'view_class': SearchCompanyView},
        {'view_class': SelectCompanyView, 'form_kwargs': {'companies': None}},
        {'view_class': ContactDetailsView},
        {'view_class': TradeEventDetailsView},
        {'view_class': CompanyTradingDetailsView},
        {'view_class': ExportExperienceView},
        {'view_class': StateAidSummaryView},
    ]

    def generate_application_summary(self):
        application_summary = []

        url = BeforeYouStartView(object=self.object).get_success_url()

        for view in self.grant_application_flow:
            summary = generate_grant_application_summary(
                grant_application=self.object,
                form_class=view['view_class'].form_class,
                form_kwargs=view.get('form_kwargs', {}),
                url=url
            )
            if summary:
                application_summary.append({
                    'heading': str(view['view_class'].static_context['page']['heading']),
                    'summary': summary
                })
            url = view['view_class'](object=self.object).get_success_url()

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


class ConfirmationView(StaticContextMixin, TemplateView):
    template_name = 'grant_applications/confirmation.html'
    static_context = {
        'page': {
            'panel_title': _('Application complete'),
            'panel_ref_text': _('Your reference number'),
            'confirmation_email_text': _('We have sent you a confirmation email.'),
            'next_steps_heading': _('What happens next'),
            'next_steps_line_1': _("We've sent your application to the Trade Access Program team."),
            'next_steps_line_2': _('They will contact you either to confirm your registration, or '
                                   'to ask for more information.'),
        }
    }
