from django.urls import path
from django.views.generic import TemplateView

from web.grant_applications.views import (
    SearchCompanyView, SelectCompanyView, ConfirmationView, AboutYourBusinessView, AboutYouView,
    AboutTheEventView, ApplicationReviewView, PreviousApplicationsView, EventIntentionView,
    BusinessInformationView, StateAidView, ExportExperienceView
)

app_name = 'grant_applications'

urlpatterns = [
    path('', TemplateView.as_view(template_name='grant_applications/index.html'), name='index'),
    path('search-company/', SearchCompanyView.as_view(), name='search-company'),
    path('select-company/', SelectCompanyView.as_view(), name='select-company'),
    path('<pk>/about-your-business/', AboutYourBusinessView.as_view(), name='about-your-business'),
    path('<pk>/about-you/', AboutYouView.as_view(), name='about-you'),
    path('<pk>/about-the-event/', AboutTheEventView.as_view(), name='about-the-event'),
    path(
        '<pk>/previous-applications/',
        PreviousApplicationsView.as_view(),
        name='previous-applications'
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
    path('<pk>/confirmation/<process_pk>/', ConfirmationView.as_view(), name='confirmation'),
]
