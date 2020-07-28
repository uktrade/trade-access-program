from django.utils.decorators import method_decorator
from viewflow import flow, frontend
from viewflow.base import this, Flow
from viewflow.flow.views import UpdateProcessView

from web.apply.models import ApplicationProcess
from web.core.notify import NotifyService


@frontend.register
class ApplyFlow(Flow):
    process_class = ApplicationProcess

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
    def start_callback(self, activation, fields):
        activation.prepare()

        for field, value in fields.items():
            setattr(activation.process, field, value)

        activation.done()

        return activation.process

    def send_application_submitted_email_callback(self, activation):
        NotifyService().send_application_submitted_email(
            email_address=activation.process.applicant_email,
            applicant_full_name=activation.process.applicant_full_name
        )
