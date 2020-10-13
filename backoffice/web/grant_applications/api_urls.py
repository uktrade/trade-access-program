from rest_framework.routers import SimpleRouter

from web.grant_applications.apis import GrantApplicationsViewSet

router = SimpleRouter()
router.register('grant-applications', GrantApplicationsViewSet, basename='grant-applications')

app_name = 'grant-applications'

urlpatterns = router.urls
