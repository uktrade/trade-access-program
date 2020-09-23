from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from web.grant_applications.models import GrantApplication
from web.grant_applications.serializers import (
    GrantApplicationReadSerializer, GrantApplicationWriteSerializer
)


class GrantApplicationsViewSet(ModelViewSet):
    queryset = GrantApplication.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return GrantApplicationWriteSerializer
        return GrantApplicationReadSerializer

    @action(detail=True, methods=['POST'], url_path='send-for-review')
    def send_for_review(self, request, pk=None):
        instance = self.get_object()
        instance.send_for_review()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
