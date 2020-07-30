from django.utils.decorators import method_decorator
from viewflow import flow, frontend
from viewflow.base import this, Flow
from viewflow.flow.views import UpdateProcessView

from web.grant_management.models import GrantApplicationProcess
from web.core.notify import NotifyService


@frontend.register
class GrantApplicationFlow(Flow):
    process_class = GrantApplicationProcess

    start = flow.StartFunction(
        this.start_callback, task_title='Submit your application.'
    ).Next(this.send_application_submitted_email)

    send_application_submitted_email = flow.Handler(
        this.send_application_submitted_email_callback
    ).Next(this.approval)

    approval = flow.View(
        UpdateProcessView, fields=['approved']
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
