from django.utils.decorators import method_decorator
from viewflow import flow, frontend
from viewflow.base import this, Flow
from viewflow.models import Task

from web.core.notify import NotifyService
from web.core.utils import generate_frontend_action_magic_link
from web.grant_management.forms import (
    VerifyPreviousApplicationsForm, VerifyBusinessEntityForm,
    VerifyEventCommitmentForm, VerifyStateAidForm, ProductsAndServicesForm, ExportStrategyForm,
    ProductsAndServicesCompetitorsForm, DecisionForm, EventIsAppropriateForm, EventBookingDocumentRenewForm
)
from web.grant_management.models import GrantManagementProcess
from web.grant_management.views import BaseGrantManagementView


@frontend.register
class GrantManagementFlow(Flow):
    notify_service = NotifyService()

    summary_template = "{{ process.grant_application.company.name" \
                       "|default:process.grant_application.manual_company_name }} " \
                       "[{{ process.status }}]"

    process_class = GrantManagementProcess

    start = flow.StartFunction(
        this.start_callback, task_title='Submit your application.'
    ).Next(this.send_application_submitted_email)

    send_application_submitted_email = flow.Handler(
        this.send_application_submitted_email_callback
    ).Next(this.create_verify_tasks)

    # Verify Eligibility tasks
    create_verify_tasks = (
        flow.Split()
        .Always(this.verify_previous_applications)
        .Always(this.verify_event_commitment)
        .Always(this.verify_business_entity)
        .Always(this.verify_state_aid)
        .Always(this.finish_verify_tasks)
    )

    verify_previous_applications = flow.View(
        BaseGrantManagementView,
        form_class=VerifyPreviousApplicationsForm,
        task_title='Verify number of previous grants'
    ).Next(this.finish_verify_tasks)

    verify_event_commitment = flow.View(
        BaseGrantManagementView,
        form_class=VerifyEventCommitmentForm,
        task_title='Verify event commitment'
    ).Next(this.finish_verify_tasks)

    verify_business_entity = flow.View(
        BaseGrantManagementView,
        form_class=VerifyBusinessEntityForm,
        task_title='Verify business eligibility'
    ).Next(this.finish_verify_tasks)

    verify_state_aid = flow.View(
        BaseGrantManagementView,
        form_class=VerifyStateAidForm,
        task_title='Verify state eligibility'
    ).Next(this.finish_verify_tasks)

    finish_verify_tasks = flow.Join().Next(this.request_event_booking_evidence)

    request_event_booking_evidence = flow.View(
        BaseGrantManagementView,
        task_title='Request proof of event booking'
    ).Next(this.send_event_booking_evidence_request_email_handler)

    send_event_booking_evidence_request_email_handler = flow.Handler(
        this.send_event_booking_evidence_request_email_callback
    ).Next(this.create_review_evidence_task)

    create_review_evidence_task = flow.Function(
        this.create_review_evidence_of_event_booking,
        task_loader=this.get_create_review_evidence_task,
        task_title='Review proof of event booking'
    ).Next(this.renew_proof_of_event_booking)

    renew_proof_of_event_booking = flow.View(
        BaseGrantManagementView,
        form_class=EventBookingDocumentRenewForm,
        task_title='Review proof of event booking'
    ).Next(this.renew_proof_of_event_booking_handler)

    renew_proof_of_event_booking_handler = flow.Handler(
        this.send_renew_proof_of_event_booking_response_email_callback
    ).Next(this.create_suitability_tasks)

    # Suitability tasks
    create_suitability_tasks = (
        flow.Split()
            .Always(this.products_and_services)
            .Always(this.products_and_services_competitors)
            .Always(this.export_strategy)
            .Always(this.event_is_appropriate)
            .Always(this.finish_suitability_tasks)
    )

    products_and_services = flow.View(
        BaseGrantManagementView,
        form_class=ProductsAndServicesForm,
        task_title='Products and services'
    ).Next(this.finish_suitability_tasks)

    products_and_services_competitors = flow.View(
        BaseGrantManagementView,
        form_class=ProductsAndServicesCompetitorsForm,
        task_title='Products and services competitors'
    ).Next(this.finish_suitability_tasks)

    export_strategy = flow.View(
        BaseGrantManagementView,
        form_class=ExportStrategyForm,
        task_title='Export strategy'
    ).Next(this.finish_suitability_tasks)

    event_is_appropriate = flow.View(
        BaseGrantManagementView,
        form_class=EventIsAppropriateForm,
        task_title='Event is appropriate'
    ).Next(this.finish_suitability_tasks)

    finish_suitability_tasks = flow.Join().Next(this.decision)

    # Decision task
    decision = flow.View(
        BaseGrantManagementView,
        form_class=DecisionForm,
        task_title='Final review',
    ).Next(this.send_decision_email)

    send_decision_email = flow.Handler(
        this.send_decision_email_callback
    ).Next(this.end)

    end = flow.End()

    @method_decorator(flow.flow_start_func)
    def start_callback(self, activation, grant_application):
        activation.prepare()
        activation.process.grant_application = grant_application
        activation.done()
        return activation.process

    @method_decorator(flow.flow_func)
    def create_review_evidence_of_event_booking(self, activation, grant_application):
        activation.prepare()
        grant_application.is_event_evidence_uploaded = True
        grant_application.save()
        activation.process = grant_application.flow_process
        activation.done()

    def get_create_review_evidence_task(self, flow_task, grant_application, **kwargs):
        task = Task.objects.get(
            process_id=grant_application.flow_process.id,
            flow_task=flow_task
        )
        return task

    def send_application_submitted_email_callback(self, activation):
        self.notify_service.send_application_submitted_email(
            email_address=activation.process.grant_application.applicant_email,
            applicant_full_name=activation.process.grant_application.applicant_full_name,
            application_id=activation.process.grant_application.id_str
        )

    def send_decision_email_callback(self, activation):
        if activation.process.is_approved:
            self.notify_service.send_application_approved_email(
                email_address=activation.process.grant_application.applicant_email,
                applicant_full_name=activation.process.grant_application.applicant_full_name,
                application_id=activation.process.grant_application.id_str
            )
        else:
            self.notify_service.send_application_rejected_email(
                email_address=activation.process.grant_application.applicant_email,
                applicant_full_name=activation.process.grant_application.applicant_full_name,
                application_id=activation.process.grant_application.id_str
            )

    UPLOAD_EVENT_BOOKING_EVIDENCE_ACTION = 'upload-event-evidence'

    def send_event_booking_evidence_request_email_callback(self, activation):
        grant_application = activation.process.grant_application
        magic_link_data = {
            'application-backoffice-id': grant_application.id_str,
            'action-type': self.UPLOAD_EVENT_BOOKING_EVIDENCE_ACTION
        }

        magic_link = generate_frontend_action_magic_link(magic_link_data)
        self.notify_service.send_event_evidence_request_email(
            email_address=grant_application.applicant_email,
            applicant_full_name=grant_application.applicant_full_name,
            magic_link=magic_link
        )
        grant_application.is_event_evidence_requested = True
        grant_application.save()

    def send_renew_proof_of_event_booking_response_email_callback(self, activation):
        grant_application = activation.process.grant_application
        if activation.process.is_event_booking_document_approved:
            grant_application.is_event_evidence_approved = True
            grant_application.save()
            self.notify_service.send_event_booking_document_approved_email(
                email_address=grant_application.applicant_email,
                applicant_full_name=grant_application.applicant_full_name,
                application_id=grant_application.id_str
            )
        else:
            self.notify_service.send_event_booking_document_rejected_email(
                email_address=grant_application.applicant_email,
                applicant_full_name=grant_application.applicant_full_name,
                application_id=grant_application.id_str
            )
