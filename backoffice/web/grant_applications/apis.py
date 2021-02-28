from django.http import FileResponse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from web.grant_applications.models import GrantApplication, StateAid
from web.grant_applications.serializers import (
    GrantApplicationReadSerializer, GrantApplicationWriteSerializer, StateAidSerializer,
    SendForReviewWriteSerializer, SendApplicationSerializer
)
from web.core.notify import NotifyService
from web.grant_applications.services import GrantApplicationPdf


class GrantApplicationsViewSet(ModelViewSet):
    queryset = GrantApplication.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return GrantApplicationWriteSerializer
        return GrantApplicationReadSerializer

    @action(detail=True, methods=['POST'], url_path='send-for-review')
    def send_for_review(self, request, pk=None):
        instance = self.get_object()
        serializer = SendForReviewWriteSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance.send_for_review()
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['GET'], url_path='pdf')
    def pdf(self, request, pk=None):
        buffer = GrantApplicationPdf(grant_application=self.get_object()).generate()
        return FileResponse(buffer, as_attachment=True, filename='grant-application.pdf')


class StateAidViewSet(ModelViewSet):
    queryset = StateAid.objects.all()
    serializer_class = StateAidSerializer
    filterset_fields = ['grant_application']


class SendApplicationEmail(APIView):
    notification_service = NotifyService()

    def post(self, request, *args, **kwargs):
        serializer = SendApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        application_email = data.get('email')
        self.notification_service.send_application_email(
            email_address=application_email,
            template_name=data.get('email'),
            personalisation=data.get('personalisation')
        )
        return Response({}, status=200)
