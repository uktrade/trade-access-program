from django.db.models import Q
from django.db.models.functions import TruncMonth
from rest_framework import serializers

from web.trade_events.models import Event


class TradeEventSerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = '__all__'


class TradeEventsAggregatesSerializer(serializers.Serializer):
    start_date_from = serializers.DateField(write_only=True, required=True)
    total_trade_events = serializers.SerializerMethodField()
    trade_event_months = serializers.SerializerMethodField()

    def get_total_trade_events(self, obj):
        return Event.objects.filter(
            Q(start_date__gte=self.validated_data['start_date_from'])
        ).count()

    def get_trade_event_months(self, obj):
        start_dates = Event.objects.filter(
            Q(start_date__gte=self.validated_data['start_date_from'])
        ).annotate(
            month=TruncMonth('start_date')
        ).distinct().order_by(
            'month'
        ).values_list(
            'month', flat=True
        )
        return [i.strftime('%B %Y') for i in start_dates]
