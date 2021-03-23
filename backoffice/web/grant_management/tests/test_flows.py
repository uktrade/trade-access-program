from unittest.mock import patch

from web.companies.services import DnbServiceClient
from web.grant_management.flows import GrantManagementFlow
from web.grant_management.tests.helpers import GrantManagementFlowTestHelper
from web.tests.factories.grant_applications import CompletedGrantApplicationFactory
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
        self.ga = CompletedGrantApplicationFactory()

    def test_is_start_of_process(self, *mocks):
        self.assertTrue(GrantManagementFlow.start.task_type, 'START')
