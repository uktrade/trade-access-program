from django.urls import path
from rest_framework.routers import SimpleRouter

from web.grant_applications.apis import GrantApplicationsViewSet, StateAidViewSet, SendApplicationEmail

router = SimpleRouter()
router.register('grant-applications', GrantApplicationsViewSet, basename='grant-applications')
router.register('state-aid', StateAidViewSet, basename='state-aid')

app_name = 'grant-applications'
urlpatterns = [
    path('send-application-email/', SendApplicationEmail.as_view(), name='send-application-email'),
] + router.urls
