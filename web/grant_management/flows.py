from django.utils.decorators import method_decorator
from viewflow import flow, frontend
from viewflow.base import this, Flow
from viewflow.flow.views import UpdateProcessView

from web.core.notify import NotifyService
from web.grant_management.models import GrantManagementProcess


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
        UpdateProcessView
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
            applicant_full_name=activation.process.grant_application.applicant_full_name
        )
