from unittest.mock import patch, create_autospec

from web.companies.services import DnbServiceClient
from web.core.notify import NotifyService
from web.grant_management.flows import GrantManagementFlow
from web.grant_management.models import GrantManagementProcess
from web.grant_management.tests.helpers import GrantManagementFlowTestHelper
from web.tests.factories.grant_applications import GrantApplicationFactory
from web.tests.factories.users import UserFactory
from web.tests.helpers import BaseTestCase


@patch.object(
    DnbServiceClient, 'get_company',
    return_value={
        'primary_name': 'company-1',
        'is_employees_number_estimated': True,
        'employee_number': 1,
        'annual_sales': 100,
    }
)
@patch('web.grant_management.flows.NotifyService')
class TestGrantManagementFlow(GrantManagementFlowTestHelper, BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user = UserFactory(is_superuser=True)
        self.ga = GrantApplicationFactory()

    def test_is_start_of_process(self, *mocks):
        self.assertTrue(GrantManagementFlow.start.task_type, 'START')

    def test_start_flow_sends_email_notification(self, *mocks):
        notify_service = create_autospec(NotifyService)
        mocks[0].return_value = notify_service
        GrantManagementFlow.start.run(grant_application=self.ga)
        notify_service.send_application_submitted_email.assert_called_once_with(
            email_address=self.ga.applicant_email,
            applicant_full_name=self.ga.applicant_full_name,
            application_id=self.ga.id_str,
        )

    def test_grant_management_happy_path(self, *mocks):
        notify_service = create_autospec(NotifyService)
        mocks[0].return_value = notify_service

        self.client.force_login(self.user)

        # start flow and step through to end of flow
        ga_process = self._start_process_and_step_through_until()

        # Grant approved email should have been sent
        notify_service.send_application_approved_email.assert_called()
        notify_service.send_application_rejected_email.assert_not_called()

        # All tasks should be completed
        self.assertFalse(ga_process.active_tasks().exists())

        # Process should be marked as finished
        self.assertIsNotNone(ga_process.finished)

    def test_grant_management_rejection(self, *mocks):
        notify_service = create_autospec(NotifyService)
        mocks[0].return_value = notify_service

        self.client.force_login(self.user)

        # start flow
        ga_process = self._start_process_and_step_through_until('decision')

        # Reject applicant
        next_task = ga_process.active_tasks().first()  # Next task should be the decision task
        self.assertEqual(next_task.flow_task.name, 'decision')
        self._assign_task(ga_process, next_task)
        self._complete_task(
            ga_process, next_task, data={'decision': GrantManagementProcess.Decision.REJECTED}
        )

        # Rejection email should have been sent
        notify_service.send_application_rejected_email.assert_called()
        notify_service.send_application_approved_email.assert_not_called()

        # All tasks should be completed
        self.assertFalse(ga_process.active_tasks().exists())

        # Process should be marked as finished
        self.assertIsNotNone(ga_process.finished)

    def test_grant_management_decision_cannot_be_empty(self, *mocks):
        self.client.force_login(self.user)

        ga_process = self._start_process_and_step_through_until('decision')

        # Next task should be the decision task
        next_task = ga_process.active_tasks().first()
        self.assertEqual(next_task.flow_task.name, 'decision')

        # Try to reject applicant
        self._assign_task(ga_process, next_task)
        response, _ = self._complete_task(ga_process, next_task, make_asserts=False)

        self.assertFormError(response, 'form', 'decision', 'This field is required.')

        # Task should not be completed
        self.assertIsNone(next_task.finished)
