from django.http import FileResponse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from web.grant_applications.models import GrantApplication, StateAid
from web.grant_applications.serializers import (
    GrantApplicationReadSerializer, GrantApplicationWriteSerializer, StateAidSerializer,
    SendForReviewWriteSerializer, SendApplicationMagicLinkSerializer
)
from web.core.notify import NotifyService
from web.grant_applications.services import GrantApplicationPdf
from web.grant_management.flows import GrantManagementFlow


class GrantApplicationsViewSet(ModelViewSet):
    queryset = GrantApplication.objects.all()
    notification_service = NotifyService()

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

    @action(detail=True, methods=['POST'], url_path='event-evidence-upload-confirmation')
    def event_evidence_upload_confirmation(self, request, pk=None):
        grant_application = self.get_object()
        if not grant_application.is_event_evidence_uploaded:
            email_data = {
                'applicant_full_name': grant_application.applicant_full_name,
                'application_id': grant_application.id_str,
                'event_name': grant_application.event.name,
            }
            self.notification_service.send_event_evidence_upload_confirmation_email(
                email_address=grant_application.applicant_email,
                email_data=email_data
            )

            # Initialise grant management tasks
            GrantManagementFlow.create_review_evidence_task.run(
                grant_application=grant_application
            )
        return Response({}, status=200)

    @action(detail=True, methods=['GET'], url_path='pdf')
    def pdf(self, request, pk=None):
        buffer = GrantApplicationPdf(grant_application=self.get_object()).generate()
        return FileResponse(buffer, as_attachment=True, filename='grant-application.pdf')


class StateAidViewSet(ModelViewSet):
    queryset = StateAid.objects.all()
    serializer_class = StateAidSerializer
    filterset_fields = ['grant_application']


class SendApplicationResumeEmailView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = SendApplicationMagicLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        application_email = data.get('email')
        personalisation = data.get('personalisation')
        notification_service = NotifyService()
        notification_service.send_application_resume_email(
            email_address=application_email,
            magic_link=personalisation.get('magic_link')
        )
        return Response({}, status=200)
