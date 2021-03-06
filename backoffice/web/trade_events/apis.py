from django_filters.rest_framework import (
    DjangoFilterBackend, FilterSet, DateFromToRangeFilter
)
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from web.trade_events.models import Event
from web.trade_events.serializers import TradeEventSerializer, TradeEventsAggregatesSerializer


class TradeEventsFilterSet(FilterSet):
    start_date_range = DateFromToRangeFilter(field_name='start_date')
    end_date_range = DateFromToRangeFilter(field_name='end_date')

    class Meta:
        model = Event
        fields = [
            'start_date', 'end_date', 'start_date_range', 'end_date_range',
            'name', 'country', 'sector'
        ]


class TradeEventsViewSet(ReadOnlyModelViewSet):
    queryset = Event.objects.all().order_by('country', 'city')
    serializer_class = TradeEventSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TradeEventsFilterSet
    search_fields = ['name']
    page_size_query_param = 'page_size'


class TradeEventsAggregatesView(APIView):

    def get(self, request, *args, **kwargs):
        serializer = TradeEventsAggregatesSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
