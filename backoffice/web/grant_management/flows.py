from django.utils.decorators import method_decorator
from viewflow import flow, frontend
from viewflow.base import this, Flow

from web.core.notify import NotifyService
from web.core.utils import generate_frontend_action_magic_link
from web.grant_management.forms import (
    VerifyPreviousApplicationsForm, VerifyBusinessEntityForm,
    VerifyEventCommitmentForm, VerifyStateAidForm, ProductsAndServicesForm, ExportStrategyForm,
    ProductsAndServicesCompetitorsForm, DecisionForm, EventIsAppropriateForm
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

    finish_verify_tasks = flow.Join().Next(this.create_suitability_tasks)

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

    def send_event_booking_evidence_request_email_callback(self, activation):
        magic_link = generate_frontend_action_magic_link()
