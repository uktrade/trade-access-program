from rest_framework.viewsets import ReadOnlyModelViewSet

from web.trade_events.models import Event
from web.trade_events.serializers import EventSerializer


class TradeEventsViewSet(ReadOnlyModelViewSet):
    queryset = Event.objects.all().order_by('country', 'city')
    serializer_class = EventSerializer
    filterset_fields = ['start_date', 'country', 'sector']
