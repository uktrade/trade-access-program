from django.urls import path
from django.views.generic import TemplateView

from web.grant_applications.views import (
    SearchCompanyView, SelectCompanyView, AboutYouView, SelectAnEventView,
    PreviousApplicationsView, EventIntentionView, BusinessInformationView, ExportExperienceView,
    StateAidView, ApplicationReviewView, ConfirmationView, EligibilityReviewView, EventFinanceView,
    EligibilityConfirmationView, BusinessDetailsView, FindAnEventView
)

app_name = 'grant_applications'

urlpatterns = [
    path('', TemplateView.as_view(template_name='grant_applications/index.html'), name='index'),
    path(
        'before-you-start',
        TemplateView.as_view(template_name='grant_applications/before-you-start.html'),
        name='before-you-start'
    ),
    path('search-company/', SearchCompanyView.as_view(), name='search-company'),
    path('<pk>/select-company/', SelectCompanyView.as_view(), name='select-company'),
    path('<pk>/business-details/', BusinessDetailsView.as_view(), name='business-details'),
    path('<pk>/about-you/', AboutYouView.as_view(), name='about-you'),
    path('<pk>/find-an-event/', FindAnEventView.as_view(), name='find-an-event'),
    path('<pk>/select-an-event/', SelectAnEventView.as_view(), name='select-an-event'),
    path('<pk>/event-finance/', EventFinanceView.as_view(), name='event-finance'),
    path(
        '<pk>/previous-applications/',
        PreviousApplicationsView.as_view(),
        name='previous-applications'
    ),
    path('<pk>/eligibility-review/', EligibilityReviewView.as_view(), name='eligibility-review'),
    path(
        '<pk>/eligibility-confirmation/',
        EligibilityConfirmationView.as_view(),
        name='eligibility-confirmation'
    ),
    path('<pk>/event-intention/', EventIntentionView.as_view(), name='event-intention'),
    path(
        '<pk>/business-information/',
        BusinessInformationView.as_view(),
        name='business-information'
    ),
    path('<pk>/export-experience/', ExportExperienceView.as_view(), name='export-experience'),
    path('<pk>/state-aid/', StateAidView.as_view(), name='state-aid'),
    path('<pk>/application-review/', ApplicationReviewView.as_view(), name='application-review'),
    path('<pk>/confirmation/', ConfirmationView.as_view(), name='confirmation'),
]
