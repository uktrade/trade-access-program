from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ReadOnlyModelViewSet

from web.trade_events.models import Event
from web.trade_events.serializers import EventSerializer


class TradeEventsViewSet(ReadOnlyModelViewSet):
    queryset = Event.objects.all().order_by('country', 'city')
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'start_date', 'country', 'sector']
    search_fields = ['name']
