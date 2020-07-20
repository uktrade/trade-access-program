from django.urls import path

from web.apply.views import SearchCompanyView, SelectCompanyView, ConfirmationView

app_name = 'apply'

urlpatterns = [
    path('search-company/', SearchCompanyView.as_view(), name='search-company'),
    path('select-company/', SelectCompanyView.as_view(), name='select-company'),
    path('<int:process_pk>/confirmation/', ConfirmationView.as_view(), name='confirmation'),
]
