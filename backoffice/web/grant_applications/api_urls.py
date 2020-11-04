from rest_framework.routers import SimpleRouter

from web.grant_applications.apis import GrantApplicationsViewSet, StateAidViewSet

router = SimpleRouter()
router.register('grant-applications', GrantApplicationsViewSet, basename='grant-applications')
router.register('state-aid', StateAidViewSet, basename='state-aid')

app_name = 'grant-applications'

urlpatterns = router.urls
