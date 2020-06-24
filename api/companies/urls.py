from rest_framework.routers import SimpleRouter

from api.companies.views import CompaniesViewSet

router = SimpleRouter()
router.register('companies', CompaniesViewSet, basename='companies')

urlpatterns = router.urls
