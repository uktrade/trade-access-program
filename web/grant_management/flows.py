from django.utils.decorators import method_decorator
from viewflow import flow, frontend
from viewflow.base import this, Flow

from web.core.notify import NotifyService
from web.grant_management.models import GrantManagementProcess
from web.grant_management.views import ApplicationAcknowledgementView, VerifyEmployeeCountView, \
    VerifyTurnoverView, DecisionView


@frontend.register
class GrantManagementFlow(Flow):
    summary_template = "{{ flow_class.process_title }} [{{ process.status }}]"
    process_class = GrantManagementProcess

    start = flow.StartFunction(
        this.start_callback, task_title='Submit your application.'
    ).Next(this.send_application_submitted_email)

    send_application_submitted_email = flow.Handler(
        this.send_application_submitted_email_callback
    ).Next(this.application_acknowledgement)

    application_acknowledgement = flow.View(
        ApplicationAcknowledgementView
    ).Next(this.verify_employee_count)

    verify_employee_count = flow.View(
        VerifyEmployeeCountView
    ).Next(this.verify_turnover)

    verify_turnover = flow.View(
        VerifyTurnoverView
    ).Next(this.decision)

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
