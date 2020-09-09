from rest_framework import serializers

from web.trade_events.models import Event


class EventSerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = '__all__'
