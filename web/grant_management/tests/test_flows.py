from unittest.mock import patch, create_autospec

from django.urls import reverse
from rest_framework.status import HTTP_200_OK

from web.companies.services import DnbServiceClient
from web.core.notify import NotifyService
from web.grant_management.flows import GrantManagementFlow
from web.tests.factories.grant_applications import GrantApplicationFactory
from web.tests.factories.users import UserFactory
from web.tests.helpers import BaseTestCase


@patch.object(
    DnbServiceClient, 'get_company',
    return_value={
        'primary_name': 'company-1', 'is_employees_number_estimated': True, 'employee_number': 1
    }
)
@patch('web.grant_management.flows.NotifyService')
class TestGrantManagementFlow(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user = UserFactory(is_superuser=True)
        self.ga = GrantApplicationFactory(duns_number=1)

    def test_is_start_of_process(self, *mocks):
        self.assertTrue(GrantManagementFlow.start.task_type, 'START')

    def test_start_flow_sends_email_notification(self, *mocks):
        notify_service = create_autospec(NotifyService)
        mocks[0].return_value = notify_service
        GrantManagementFlow.start.run(grant_application=self.ga)
        notify_service.send_application_submitted_email.assert_called()

    def _assign_next_task(self, process, task_name):
        # Get next task
        next_task = process.active_tasks().first()

        # Check it is what we expect
        self.assertIsNone(next_task.assigned)
        self.assertEqual(next_task.flow_task.name, task_name)

        # Assign task to current logged in user
        self.apl_ack_assign_url = reverse(
            f'viewflow:grant_management:grantmanagement:{next_task.flow_task.name}__assign',
            kwargs={'process_pk': process.pk, 'task_pk': next_task.pk},
        )
        assign_response = self.client.post(self.apl_ack_assign_url, follow=True)
        self.assertEqual(assign_response.status_code, HTTP_200_OK)

        # Check task is assigned
        next_task.refresh_from_db()
        self.assertIsNotNone(next_task.assigned)

        return next_task

    def _complete_task(self, process, task, data=None):
        self.apl_ack_task_url = reverse(
            f'viewflow:grant_management:grantmanagement:{task.flow_task.name}',
            kwargs={'process_pk': process.pk, 'task_pk': task.pk},
        )
        apl_ack_response = self.client.post(self.apl_ack_task_url, data=data, follow=True)
        self.assertEqual(apl_ack_response.status_code, HTTP_200_OK)

    def test_flow_happy_path(self, *mocks):
        self.client.force_login(self.user)

        # start flow
        ga_process = GrantManagementFlow.start.run(grant_application=self.ga)

        # Complete application acknowledgement task
        next_task = self._assign_next_task(ga_process, 'application_acknowledgement')
        self._complete_task(ga_process, next_task)

        # Complete verify employee count task
        next_task = self._assign_next_task(ga_process, 'verify_employee_count')
        self._complete_task(ga_process, next_task)

        # All tasks should be completed
        self.assertFalse(ga_process.active_tasks().exists())

        # Process should be marked as finished
        ga_process.refresh_from_db()
        self.assertIsNotNone(ga_process.finished)
