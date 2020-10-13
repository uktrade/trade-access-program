from rest_framework.routers import SimpleRouter

from web.trade_events.apis import TradeEventsViewSet

router = SimpleRouter()
router.register('trade-events', TradeEventsViewSet, basename='trade-events')

app_name = 'trade-events'
urlpatterns = router.urls
