from django.urls import path

from web.grant_applications.views import (
    SearchCompanyView, SelectCompanyView, ConfirmationView, SubmitApplicationView
)

app_name = 'grant_applications'

urlpatterns = [
    path('search-company/', SearchCompanyView.as_view(), name='search-company'),
    path('select-company/', SelectCompanyView.as_view(), name='select-company'),
    path('submit-application/', SubmitApplicationView.as_view(), name='submit-application'),
    path('<int:process_pk>/confirmation/', ConfirmationView.as_view(), name='confirmation'),
]
