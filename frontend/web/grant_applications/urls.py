from django.urls import path
from django.views.generic import TemplateView

from web.grant_applications.views import (
    SearchCompanyView, SelectCompanyView, ContactDetailsView, SelectAnEventView,
    PreviousApplicationsView, CompanyTradingDetailsView, ExportExperienceView, StateAidSummaryView,
    ApplicationReviewView, FindAnEventView, BeforeYouStartView, EventCommitmentView,
    CompanyDetailsView, ExportDetailsView, TradeEventDetailsView, AddStateAidView, EditStateAidView,
    DeleteStateAidView, DuplicateStateAidView, ManualCompanyDetailsView,
    StartNewApplicationView, MagicLinkHandlerView, SelectApplicationProgressView,
    CheckYourEmailView, InvalidMagicLinkView, ExpiredMagicLinkView,
    NoApplicationFoundView, ContinueApplicationView, ApplicationIndexView, EventEvidenceUploadView,
    EventEvidenceUploadCompleteView
)

app_name = 'grant_applications'

urlpatterns = [
    path('', ApplicationIndexView.as_view(), name='index'),
    path('before-you-start/', BeforeYouStartView.as_view(), name='before-you-start'),
    path(
        'new-application-email/',
        StartNewApplicationView.as_view(),
        name='new-application-email'
    ),
    path(
        'continue-application-email/',
        ContinueApplicationView.as_view(),
        name='continue-application-email'
    ),
    path(
        'select-application-progress/',
        SelectApplicationProgressView.as_view(),
        name='select-application-progress'
    ),
    path('check-your-email/', CheckYourEmailView.as_view(), name='check-your-email'),
    path('resume/<hash>/', MagicLinkHandlerView.as_view(), name='magic-link'),
    path('invalid-link/', InvalidMagicLinkView.as_view(), name='invalid-magic-link'),
    path('expired-link/', ExpiredMagicLinkView.as_view(), name='expired-magic-link'),
    path('no-application-found/', NoApplicationFoundView.as_view(), name='no-application-found'),
    path(
        '<pk>/previous-applications/',
        PreviousApplicationsView.as_view(),
        name='previous-applications'
    ),
    path('<pk>/find-an-event/', FindAnEventView.as_view(), name='find-an-event'),
    path('<pk>/select-an-event/', SelectAnEventView.as_view(), name='select-an-event'),
    path('<pk>/event-commitment/', EventCommitmentView.as_view(), name='event-commitment'),
    path('<pk>/search-company/', SearchCompanyView.as_view(), name='search-company'),
    path('<pk>/select-company/', SelectCompanyView.as_view(), name='select-company'),
    path(
        '<pk>/manual-company-details/',
        ManualCompanyDetailsView.as_view(),
        name='manual-company-details'
    ),
    path('<pk>/company-details/', CompanyDetailsView.as_view(), name='company-details'),
    path('<pk>/contact-details/', ContactDetailsView.as_view(), name='contact-details'),
    path(
        '<pk>/company-trading-details/',
        CompanyTradingDetailsView.as_view(),
        name='company-trading-details'
    ),
    path('<pk>/export-experience/', ExportExperienceView.as_view(), name='export-experience'),
    path('<pk>/export-details/', ExportDetailsView.as_view(), name='export-details'),
    path('<pk>/trade-event-details/', TradeEventDetailsView.as_view(), name='trade-event-details'),
    path('<pk>/state-aid-summary/', StateAidSummaryView.as_view(), name='state-aid-summary'),
    path('<pk>/add-state-aid/', AddStateAidView.as_view(), name='add-state-aid'),
    path('<pk>/edit-state-aid/<state_aid_pk>/', EditStateAidView.as_view(), name='edit-state-aid'),
    path(
        '<pk>/delete-state-aid/<state_aid_pk>/',
        DeleteStateAidView.as_view(),
        name='delete-state-aid'
    ),
    path(
        '<pk>/duplicate-state-aid/<state_aid_pk>/',
        DuplicateStateAidView.as_view(),
        name='duplicate-state-aid'
    ),
    path('<pk>/application-review/', ApplicationReviewView.as_view(), name='application-review'),
    path(
        '<pk>/confirmation/',
        TemplateView.as_view(template_name='grant_applications/confirmation.html'),
        name='confirmation'
    ),
    path(
        'ineligible/',
        TemplateView.as_view(template_name='grant_applications/ineligible.html'),
        name='ineligible'
    ),

    path(
        '<pk>/event-booking-evidence-upload/',
        EventEvidenceUploadView.as_view(),
        name='event-evidence-upload'
    ),
    path(
        '<pk>/event-booking-evidence-complete/',
        EventEvidenceUploadCompleteView.as_view(),
        name='event-evidence-upload-complete'
    )
]
