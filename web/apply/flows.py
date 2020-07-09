from viewflow import flow, frontend
from viewflow.base import this, Flow

from web.apply.models import ApplicationProcess
from web.apply.views import SubmitApplicationView


@frontend.register
class ApplyFlow(Flow):
    process_class = ApplicationProcess

    submit = flow.Start(
        SubmitApplicationView, task_title='Submit your application.'
    ).Next(this.end)

    end = flow.End()
