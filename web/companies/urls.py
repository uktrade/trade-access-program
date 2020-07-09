from django.conf.urls import url
from rest_framework.routers import SimpleRouter

from web.companies.views import CompaniesViewSet, SearchCompaniesView

router = SimpleRouter()
router.register('companies', CompaniesViewSet, basename='companies')


urlpatterns = [
    url(r'^companies/search/$', SearchCompaniesView.as_view(), name='companies-search'),
] + router.urls
