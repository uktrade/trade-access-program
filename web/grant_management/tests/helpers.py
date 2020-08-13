from django.urls import reverse
from django.utils import timezone
from rest_framework.status import HTTP_200_OK

from web.grant_management.flows import GrantManagementFlow


class GrantManagementFlowTestHelper:
    ORDERED_HUMAN_TASKS = [
        {
            'name': 'application_acknowledgement',
        },
        {
            'name': 'verify_employee_count',
            'data': {'employee_count_is_verified': True},
        },
        {
            'name': 'verify_turnover',
            'data': {'turnover_is_verified': True},
        },
        {
            'name': 'decision',
            'data': {'decision': 'approved'},
        },
        {
            'name': 'end',
        },
    ]

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
        response = self.client.post(self.apl_ack_assign_url, follow=True)
        self.assertEqual(response.status_code, HTTP_200_OK)

        # Check task is assigned
        next_task.refresh_from_db()
        self.assertIsNotNone(next_task.assigned)

        return response, next_task

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

        for human_task in self.ORDERED_HUMAN_TASKS:
            if human_task['name'] == task_name:
                ga_process.refresh_from_db()
                return ga_process
            else:
                # Complete next task
                _, next_task = self._assign_next_task(ga_process, human_task['name'])
                self._complete_task(ga_process, next_task, data=human_task.get('data'))
