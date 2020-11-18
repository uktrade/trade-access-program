from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse, resolve
from django.utils import timezone
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView, RedirectView
from django.views.generic.detail import SingleObjectMixin

from web.core.forms import FORM_MSGS
from web.core.view_mixins import SuccessUrlObjectPkMixin, BackContextMixin, PaginationMixin
from web.grant_applications.forms import (
    SearchCompanyForm, SelectCompanyForm, SelectAnEventForm, PreviousApplicationsForm,
    CompanyTradingDetailsForm, ExportExperienceForm, FindAnEventForm,
    EmptyGrantApplicationLinkForm, EventCommitmentForm, CompanyDetailsForm, ContactDetailsForm,
    ExportDetailsForm, TradeEventDetailsForm, AddStateAidForm, EditStateAidForm,
    ManualCompanyDetailsForm
)
from web.grant_applications.models import GrantApplicationLink
from web.grant_applications.services import (
    BackofficeServiceException, BackofficeService, get_companies_from_search_term,
    get_state_aid_summary_table, ApplicationReviewService
)
from web.grant_applications.view_mixins import (
    BackofficeMixin, InitialDataMixin, ConfirmationRedirectMixin, IneligibleRedirectMixin
)


class BeforeYouStartView(BackContextMixin, SuccessUrlObjectPkMixin, CreateView):
    model = GrantApplicationLink
    form_class = EmptyGrantApplicationLinkForm
    template_name = 'grant_applications/before_you_start.html'
    back_url_name = 'grant-applications:index'
    success_url_name = 'grant_applications:previous-applications'
    extra_context = {
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


class PreviousApplicationsView(BackContextMixin, SuccessUrlObjectPkMixin, BackofficeMixin,
                               InitialDataMixin, ConfirmationRedirectMixin, IneligibleRedirectMixin,
                               UpdateView):
    model = GrantApplicationLink
    form_class = PreviousApplicationsForm
    template_name = 'grant_applications/previous_applications.html'
    back_url_name = 'grant-applications:before-you-start'
    success_url_name = 'grant_applications:find-an-event'
    extra_context = {
        'page': {
            'heading':  _('Previous TAP grants')
        }
    }

    def get_back_url(self):
        return reverse(self.back_url_name)


class FindAnEventView(BackContextMixin, BackofficeMixin, ConfirmationRedirectMixin,
                      IneligibleRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = FindAnEventForm
    template_name = 'grant_applications/find_an_event.html'
    back_url_name = 'grant-applications:previous-applications'
    success_url_name = 'grant_applications:select-an-event'
    extra_context = {
        'page': {
            'heading':  _('Find an event')
        }
    }

    def get_success_url(self, **params):
        url = reverse(self.success_url_name, args=(self.object.pk,))
        if hasattr(self, 'request'):
            params = {
                'filter_by_name': self.request.POST.get('filter_by_name', ''),
                'filter_by_sector': self.request.POST.get('filter_by_sector', ''),
                'filter_by_country': self.request.POST.get('filter_by_country', ''),
                'filter_by_month': self.request.POST.get('filter_by_month', ''),
            }
            return f'{url}?{urlencode(params)}'
        return url

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


class SelectAnEventView(BackContextMixin, SuccessUrlObjectPkMixin, BackofficeMixin,
                        ConfirmationRedirectMixin, IneligibleRedirectMixin, PaginationMixin,
                        UpdateView):
    model = GrantApplicationLink
    form_class = SelectAnEventForm
    template_name = 'grant_applications/select_an_event.html'
    back_url_name = 'grant-applications:find-an-event'
    success_url_name = 'grant_applications:event-commitment'
    extra_context = {
        'page': {
            'heading':  _('Select an event')
        },
        'button_text': 'Select and continue',
    }
    events_page_size = 10
    grant_application_fields = ['event']

    def get_initial(self):
        initial = super().get_initial()
        initial['filter_by_name'] = self.request.GET.get('filter_by_name')
        initial['filter_by_country'] = self.request.GET.get('filter_by_country')
        initial['filter_by_sector'] = self.request.GET.get('filter_by_sector')
        initial['filter_by_month'] = self.request.GET.get('filter_by_month')
        if hasattr(self, 'backoffice_grant_application') \
                and self.backoffice_grant_application['event']:
            initial['event'] = self.backoffice_grant_application['event']['id']
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['trade_events'] = self.trade_events
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


class EventCommitmentView(BackContextMixin, SuccessUrlObjectPkMixin, BackofficeMixin,
                          InitialDataMixin, ConfirmationRedirectMixin, IneligibleRedirectMixin,
                          UpdateView):
    model = GrantApplicationLink
    form_class = EventCommitmentForm
    template_name = 'grant_applications/event_commitment.html'
    back_url_name = 'grant-applications:select-an-event'
    success_url_name = 'grant_applications:search-company'
    extra_context = {
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


class SearchCompanyView(BackContextMixin, BackofficeMixin, InitialDataMixin,
                        ConfirmationRedirectMixin, IneligibleRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = SearchCompanyForm
    template_name = 'grant_applications/search_company.html'
    back_url_name = 'grant-applications:event-commitment'
    extra_context = {
        'page': {
            'heading': _('Find your business')
        },
        'button_text': 'Search'
    }

    def get_success_url(self):
        url = reverse('grant-applications:select-company', args=(self.object.pk,))
        if hasattr(self, 'request'):
            return f"{url}?search_term={self.request.POST['search_term']}"
        return url


class SelectCompanyView(BackContextMixin, SuccessUrlObjectPkMixin, BackofficeMixin,
                        ConfirmationRedirectMixin, IneligibleRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = SelectCompanyForm
    template_name = 'grant_applications/select_company.html'
    back_url_name = 'grant-applications:search-company'
    success_url_name = 'grant-applications:company-details'
    extra_context = {
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

    def get_context_data(self, **kwargs):
        kwargs['number_of_matches'] = len(self.companies or [])
        return super().get_context_data(**kwargs)

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
            extra_grant_application_data={
                f: None for f in ManualCompanyDetailsForm.Meta.fields
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


class ManualCompanyDetailsView(BackContextMixin, SuccessUrlObjectPkMixin, BackofficeMixin,
                               InitialDataMixin, ConfirmationRedirectMixin, IneligibleRedirectMixin,
                               UpdateView):
    model = GrantApplicationLink
    form_class = ManualCompanyDetailsForm
    template_name = 'grant_applications/manual_company_details.html'
    back_url_name = 'grant-applications:select-company'
    success_url_name = 'grant-applications:company-details'
    extra_context = {
        'page': {
            'heading':  _('Business details')
        }
    }

    def form_valid(self, form):
        # Set company to None in case it has been set previously
        return super().form_valid(form, extra_grant_application_data={'company': None})


class CompanyDetailsView(BackContextMixin, SuccessUrlObjectPkMixin, BackofficeMixin,
                         InitialDataMixin, ConfirmationRedirectMixin, IneligibleRedirectMixin,
                         UpdateView):
    model = GrantApplicationLink
    form_class = CompanyDetailsForm
    template_name = 'grant_applications/company_details.html'
    success_url_name = 'grant-applications:contact-details'
    extra_context = {
        'page': {
            'heading':  _('Business size and turnover')
        }
    }

    def get_back_url(self):
        if self.backoffice_grant_application['company']:
            return reverse('grant-applications:select-company', args=(self.object.pk,))
        return reverse('grant-applications:manual-company-details', args=(self.object.pk,))


class ContactDetailsView(BackContextMixin, SuccessUrlObjectPkMixin, BackofficeMixin,
                         InitialDataMixin, ConfirmationRedirectMixin, IneligibleRedirectMixin,
                         UpdateView):
    model = GrantApplicationLink
    form_class = ContactDetailsForm
    template_name = 'grant_applications/contact_details.html'
    back_url_name = 'grant-applications:company-details'
    success_url_name = 'grant_applications:company-trading-details'
    extra_context = {
        'page': {
            'heading':  _('Business contact details')
        }
    }


class CompanyTradingDetailsView(BackContextMixin, SuccessUrlObjectPkMixin, BackofficeMixin,
                                InitialDataMixin, ConfirmationRedirectMixin,
                                IneligibleRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = CompanyTradingDetailsForm
    template_name = 'grant_applications/company_trading_details.html'
    back_url_name = 'grant-applications:contact-details'
    success_url_name = 'grant_applications:export-experience'
    extra_context = {
        'page': {
            'heading':  _('Business trading details')
        }
    }

    def get_initial(self):
        initial = super().get_initial()
        if self.backoffice_grant_application['sector']:
            initial['sector'] = self.backoffice_grant_application['sector']['id']
        return initial


class ExportExperienceView(BackContextMixin, BackofficeMixin, InitialDataMixin,
                           ConfirmationRedirectMixin, IneligibleRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = ExportExperienceForm
    template_name = 'grant_applications/export_experience.html'
    back_url_name = 'grant-applications:company-trading-details'
    extra_context = {
        'page': {
            'heading':  _('Export experience')
        }
    }

    def get_success_url(self):
        if self.backoffice_grant_application['has_exported_before']:
            return reverse('grant-applications:export-details', args=(self.object.pk,))

        if self.object.has_viewed_review_page:
            return reverse('grant-applications:application-review', args=(self.object.pk,))

        return reverse('grant-applications:trade-event-details', args=(self.object.pk,))

    def form_valid(self, form):
        if not form.cleaned_data['has_exported_before']:
            # Set ExportDetails form fields to None
            return super().form_valid(
                form, extra_grant_application_data={f: None for f in ExportDetailsForm.Meta.fields}
            )
        return super().form_valid(form)


class ExportDetailsView(BackContextMixin, SuccessUrlObjectPkMixin, BackofficeMixin,
                        InitialDataMixin, ConfirmationRedirectMixin, IneligibleRedirectMixin,
                        UpdateView):
    model = GrantApplicationLink
    form_class = ExportDetailsForm
    template_name = 'grant_applications/export_details.html'
    back_url_name = 'grant-applications:export-experience'
    success_url_name = 'grant_applications:trade-event-details'
    extra_context = {
        'page': {
            'heading':  _('Export details')
        }
    }


class TradeEventDetailsView(BackContextMixin, SuccessUrlObjectPkMixin, BackofficeMixin,
                            InitialDataMixin, ConfirmationRedirectMixin, IneligibleRedirectMixin,
                            UpdateView):
    model = GrantApplicationLink
    form_class = TradeEventDetailsForm
    template_name = 'grant_applications/trade_event_details.html'
    success_url_name = 'grant_applications:state-aid-summary'
    extra_context = {
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


class StateAidSummaryView(BackContextMixin, SuccessUrlObjectPkMixin, BackofficeMixin,
                          ConfirmationRedirectMixin, IneligibleRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = EmptyGrantApplicationLinkForm
    template_name = 'grant_applications/state_aid_summary.html'
    back_url_name = 'grant-applications:export-experience'
    success_url_name = 'grant_applications:application-review'
    extra_context = {
        'page': {
            'heading':  _('State aid')
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


class DeleteStateAidView(BackofficeMixin, SingleObjectMixin, ConfirmationRedirectMixin,
                         IneligibleRedirectMixin, RedirectView):
    model = GrantApplicationLink
    pattern_name = 'grant-applications:state-aid-summary'

    def get_redirect_url(self, *args, **kwargs):
        try:
            self.backoffice_service.delete_state_aid(state_aid_id=kwargs['state_aid_pk'])
        except BackofficeServiceException:
            pass
        return super().get_redirect_url(pk=self.object.pk)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class DuplicateStateAidView(BackofficeMixin, SingleObjectMixin, ConfirmationRedirectMixin,
                            IneligibleRedirectMixin, RedirectView):
    model = GrantApplicationLink
    pattern_name = 'grant-applications:state-aid-summary'

    def get_redirect_url(self, *args, **kwargs):
        try:
            state_aid = self.backoffice_service.get_state_aid(state_aid_id=kwargs['state_aid_pk'])
            self.backoffice_service.create_state_aid(
                grant_application=self.object.backoffice_grant_application_id,
                **{k: v for k, v in state_aid.items() if k in AddStateAidForm.Meta.fields}
            )
        except BackofficeServiceException:
            pass
        return super().get_redirect_url(pk=self.object.pk)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class StateAidItemMixin(BackContextMixin, BackofficeMixin, ConfirmationRedirectMixin,
                        IneligibleRedirectMixin):
    model = GrantApplicationLink
    template_name = 'grant_applications/state_aid_item.html'
    back_url_name = 'grant-applications:state-aid-summary'
    grant_application_fields = []

    def get_success_url(self):
        return reverse('grant_applications:state-aid-summary', args=(self.object.pk,))


class AddStateAidView(StateAidItemMixin, UpdateView):
    form_class = AddStateAidForm
    extra_context = {
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
    extra_context = {
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


class ApplicationReviewView(BackContextMixin, BackofficeMixin, ConfirmationRedirectMixin,
                            IneligibleRedirectMixin, UpdateView):
    model = GrantApplicationLink
    form_class = EmptyGrantApplicationLinkForm
    template_name = 'grant_applications/application_review.html'
    back_url_name = 'grant-applications:state-aid-summary'
    extra_context = {
        'page': {
            'heading':  _('Check your answers before you submit your application')
        }
    }
    sections = [
        {'url_name': 'grant-applications:previous-applications'},
        {'url_name': 'grant-applications:select-an-event'},
        {'url_name': 'grant-applications:event-commitment'},
        {'url_name': 'grant-applications:select-company'},
        {'url_name': 'grant-applications:manual-company-details'},
        {'url_name': 'grant-applications:company-details'},
        {'url_name': 'grant-applications:contact-details'},
        {'url_name': 'grant-applications:company-trading-details'},
        {'url_name': 'grant-applications:export-experience'},
        {'url_name': 'grant-applications:export-details'},
        {'url_name': 'grant-applications:trade-event-details'},
        {'url_name': 'grant-applications:state-aid-summary'},
    ]

    def get_success_url(self):
        return reverse('grant-applications:confirmation', args=(self.object.pk,))

    def generate_application_summary(self):
        service = ApplicationReviewService(
            grant_application_link=self.object,
            application_data=self.backoffice_grant_application
        )

        application_summary = []

        for section in self.sections:
            url = reverse(section['url_name'], args=(self.object.pk,))
            view_class = resolve(url).func.view_class
            form = view_class.form_class(data=self.backoffice_grant_application)
            method_name = f"{section['url_name'].split(':')[-1].replace('-', '_')}_summary_list"
            method = getattr(service, method_name, service.generic_summary_list)
            summary_list = method(
                heading=str(view_class.extra_context['page']['heading']),
                fields=form.visible_fields(),
                url=url
            )
            if summary_list:
                application_summary.append(summary_list)

        return application_summary

    def get_context_data(self, **kwargs):
        kwargs['application_summary'] = self.generate_application_summary()
        self.request.session['application_summary'] = kwargs['application_summary']
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        try:
            self.backoffice_service.send_grant_application_for_review(
                str(self.object.backoffice_grant_application_id),
                application_summary=self.request.session['application_summary']
            )
        except BackofficeServiceException:
            msg = forms.ValidationError(FORM_MSGS['resubmit'])
            form.add_error(None, msg)
            return super().form_invalid(form)
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = super().get(request, *args, **kwargs)
        self.object.has_viewed_review_page = True
        self.object.save()
        return response
