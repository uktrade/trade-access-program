from django.urls import path
from rest_framework.routers import SimpleRouter

from web.grant_applications.apis import GrantApplicationsViewSet, StateAidViewSet, SendApplicationResumeEmailView

router = SimpleRouter()
router.register('grant-applications', GrantApplicationsViewSet, basename='grant-applications')
router.register('state-aid', StateAidViewSet, basename='state-aid')

app_name = 'grant-applications'
urlpatterns = [
    path('send-resume-application-email/', SendApplicationResumeEmailView.as_view(), name='send-application-email'),
] + router.urls
