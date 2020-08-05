from unittest.mock import patch, create_autospec

from django.urls import reverse
from rest_framework.status import HTTP_200_OK

from web.core.notify import NotifyService
from web.grant_management import services
from web.grant_management.flows import GrantManagementFlow
from web.tests.factories.grant_applications import GrantApplicationFactory
from web.tests.factories.users import UserFactory
from web.tests.helpers import BaseTestCase


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
        services.start_flow(self.ga)
        notify_service.send_application_submitted_email.assert_called()

    def test_flow_happy_path(self, *mocks):
        self.client.force_login(self.user)

        # start flow
        ga_process = services.start_flow(self.ga)

        # Assign application acknowledgement task to current logged in user
        next_task = ga_process.active_tasks().first()
        self.assertIsNone(next_task.assigned)

        self.apl_ack_assign_url = reverse(
            'viewflow:grant_management:grantmanagement:application_acknowledgement__assign',
            kwargs={'process_pk': ga_process.pk, 'task_pk': next_task.pk},
        )
        assign_response = self.client.post(self.apl_ack_assign_url, follow=True)

        next_task.refresh_from_db()
        self.assertEqual(assign_response.status_code, HTTP_200_OK)
        self.assertIsNotNone(next_task.assigned)

        # Render application acknowledgement task page
        self.apl_ack_task_url = reverse(
            'viewflow:grant_management:grantmanagement:application_acknowledgement',
            kwargs={'process_pk': ga_process.pk, 'task_pk': next_task.pk},
        )
        apl_ack_response = self.client.get(self.apl_ack_task_url)
        self.assertEqual(apl_ack_response.status_code, HTTP_200_OK)

        # Complete application acknowledgement task
        self.apl_ack_task_url = reverse(
            'viewflow:grant_management:grantmanagement:application_acknowledgement',
            kwargs={'process_pk': ga_process.pk, 'task_pk': next_task.pk},
        )
        apl_ack_response = self.client.post(self.apl_ack_task_url, follow=True)
        self.assertEqual(apl_ack_response.status_code, HTTP_200_OK)

        # All tasks should be completed
        self.assertFalse(ga_process.active_tasks().exists())

        # Process should be marked as finished
        ga_process.refresh_from_db()
        self.assertIsNotNone(ga_process.finished)
