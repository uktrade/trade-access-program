from django.urls import path

from web.grant_applications.views import (
    SearchCompanyView, SelectCompanyView, ConfirmationView, AboutYourBusinessView, AboutYouView,
    AboutTheEventView, ApplicationReviewView
)

app_name = 'grant_applications'

urlpatterns = [
    path('search-company/', SearchCompanyView.as_view(), name='search-company'),
    path('select-company/', SelectCompanyView.as_view(), name='select-company'),
    path('<pk>/about-your-business/', AboutYourBusinessView.as_view(), name='about-your-business'),
    path('<pk>/about-you/', AboutYouView.as_view(), name='about-you'),
    path('<pk>/about-the-event/', AboutTheEventView.as_view(), name='about-the-event'),
    path('<pk>/application-review/', ApplicationReviewView.as_view(), name='application-review'),
    path('<pk>/confirmation/<process_pk>/', ConfirmationView.as_view(), name='confirmation'),
]
