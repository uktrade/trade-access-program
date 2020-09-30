from rest_framework.routers import SimpleRouter

from web.sectors.apis import SectorsViewSet

router = SimpleRouter()
router.register('sectors', SectorsViewSet, basename='sectors')

urlpatterns = router.urls
