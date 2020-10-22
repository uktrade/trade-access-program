from django.urls import path
from rest_framework.routers import SimpleRouter

from web.trade_events.apis import TradeEventsViewSet, TradeEventsAggregatesView

router = SimpleRouter()
router.register('trade-events', TradeEventsViewSet, basename='trade-events')

app_name = 'trade-events'
urlpatterns = [
    path('trade-events/aggregates/', TradeEventsAggregatesView.as_view(), name='aggregate'),
] + router.urls
