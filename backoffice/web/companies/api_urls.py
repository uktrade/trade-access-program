from django.urls import path
from rest_framework.routers import SimpleRouter

from web.companies.apis import CompaniesViewSet, SearchCompaniesView

router = SimpleRouter()
router.register('companies', CompaniesViewSet, basename='companies')

app_name = 'companies'

urlpatterns = [
    path('companies/search/', SearchCompaniesView.as_view(), name='search'),
] + router.urls
