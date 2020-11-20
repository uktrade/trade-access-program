from django.utils.decorators import method_decorator
from viewflow import flow, frontend
from viewflow.base import this, Flow

from web.core.notify import NotifyService
from web.grant_management.models import GrantManagementProcess
from web.grant_management.views import (
    VerifyPreviousApplicationsView, VerifyEventCommitmentView, VerifyBusinessEntityView,
    VerifyStateAidView, ProductsAndServicesView, DecisionView
)


@frontend.register
class GrantManagementFlow(Flow):
    summary_template = "{{ process.grant_application.company.name }} [{{ process.status }}]"
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
        VerifyPreviousApplicationsView
    ).Next(this.finish_verify_tasks)

    verify_event_commitment = flow.View(
        VerifyEventCommitmentView
    ).Next(this.finish_verify_tasks)

    verify_business_entity = flow.View(
        VerifyBusinessEntityView
    ).Next(this.finish_verify_tasks)

    verify_state_aid = flow.View(
        VerifyStateAidView
    ).Next(this.finish_verify_tasks)

    finish_verify_tasks = flow.Join().Next(this.create_suitability_tasks)

    # Suitability tasks
    create_suitability_tasks = (
        flow.Split()
            .Always(this.products_and_services)
            .Always(this.finish_suitability_tasks)
    )

    products_and_services = flow.View(
        ProductsAndServicesView
    ).Next(this.finish_suitability_tasks)

    finish_suitability_tasks = flow.Join().Next(this.decision)

    # Decision task
    decision = flow.View(
        DecisionView
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
        NotifyService().send_application_submitted_email(
            email_address=activation.process.grant_application.applicant_email,
            applicant_full_name=activation.process.grant_application.applicant_full_name,
            application_id=activation.process.grant_application.id_str
        )

    def send_decision_email_callback(self, activation):
        if activation.process.is_approved:
            NotifyService().send_application_approved_email(
                email_address=activation.process.grant_application.applicant_email,
                applicant_full_name=activation.process.grant_application.applicant_full_name,
                application_id=activation.process.grant_application.id_str
            )
        else:
            NotifyService().send_application_rejected_email(
                email_address=activation.process.grant_application.applicant_email,
                applicant_full_name=activation.process.grant_application.applicant_full_name,
                application_id=activation.process.grant_application.id_str
            )
