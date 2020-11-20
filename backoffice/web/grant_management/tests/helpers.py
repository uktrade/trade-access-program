from django.urls import reverse
from django.utils import timezone
from rest_framework.status import HTTP_200_OK

from web.grant_management.flows import GrantManagementFlow
from web.grant_management.models import GrantManagementProcess


class GrantManagementFlowTestHelper:
    DEFAULT_TASK_PAYLOADS = {
        'verify_previous_applications': {'previous_applications_is_verified': True},
        'verify_event_commitment': {'event_commitment_is_verified': True},
        'verify_business_entity': {'business_entity_is_verified': True},
        'verify_state_aid': {'state_aid_is_verified': False},
        'products_and_services': {
            'products_and_services_score': 5,
            'products_and_services_justification': 'Blah blah blah'
        },
        'products_and_services_competitors': {
            'products_and_services_competitors_score': 5,
            'products_and_services_competitors_justification': 'Blah blah blah'
        },
        'export_strategy': {
            'export_strategy_score': 5,
            'export_strategy_justification': 'Blah blah blah'
        },
        'event_is_appropriate': {'event_is_appropriate': True},
        'decision': {'decision': GrantManagementProcess.Decision.APPROVED},
    }

    def _assign_task(self, process, task):
        # Check task is unassigned
        self.assertIsNone(task.assigned)

        # Assign task to current logged in user
        self.apl_ack_assign_url = reverse(
            f'viewflow:grant_management:grantmanagement:{task.flow_task.name}__assign',
            kwargs={'process_pk': process.pk, 'task_pk': task.pk},
        )
        response = self.client.post(self.apl_ack_assign_url, follow=True)
        self.assertEqual(response.status_code, HTTP_200_OK)

        # Check task is assigned
        task.refresh_from_db()
        self.assertIsNotNone(task.assigned)

        return response, task

    def _complete_task(self, process, task, data=None, make_asserts=True):
        data = data or {}
        # Required as explained here https://github.com/viewflow/viewflow/issues/100
        data['_viewflow_activation-started'] = timezone.now().strftime("%Y-%m-%d %H:%M")

        self.apl_ack_task_url = reverse(
            f'viewflow:grant_management:grantmanagement:{task.flow_task.name}',
            kwargs={'process_pk': process.pk, 'task_pk': task.pk},
        )

        response = self.client.post(self.apl_ack_task_url, data=data, follow=True)
        task.refresh_from_db()
        process.refresh_from_db()

        if make_asserts:
            if 'form' in getattr(response, 'context_data', {}):
                self.assertTrue(
                    response.context_data['form'].is_valid(),
                    msg=response.context_data['form'].errors.as_data()
                )

            self.assertIsNotNone(task.finished)

        return response, task

    def _start_process_and_step_through_until(self, task_name='end'):
        """
            Helper method to step through the process flow up to the provided task_name.

            If task_name not provided step through until end of process flow.
        """
        # start flow
        ga_process = GrantManagementFlow.start.run(grant_application=self.ga)

        # Get next task
        next_task = ga_process.active_tasks().first()

        while next_task and next_task.flow_task.name != task_name:
            # Complete next task if it is a HUMAN task
            if next_task.flow_task_type == 'HUMAN':
                _, next_task = self._assign_task(ga_process, next_task)
                self._complete_task(
                    ga_process, next_task,
                    data=self.DEFAULT_TASK_PAYLOADS.get(next_task.flow_task.name)
                )
            # Get next task
            next_task = ga_process.active_tasks().first()

        ga_process.refresh_from_db()
        return ga_process
