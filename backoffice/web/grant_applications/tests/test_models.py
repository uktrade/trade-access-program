from unittest.mock import patch

from web.grant_applications.models import GrantApplication
from web.tests.factories.grant_applications import GrantApplicationFactory
from web.tests.helpers import BaseTestCase


@patch('web.grant_management.flows.NotifyService')
class TestGrantApplicationModel(BaseTestCase):

    def test_send_for_review_starts_flow_process(self, *mocks):
        ga = GrantApplicationFactory()
        ga.send_for_review()
        self.assertTrue(hasattr(ga, 'grant_management_process'))

    def test_number_of_employees_choices(self, *mocks):
        self.assertEqual(
            GrantApplication.NumberOfEmployees.get_choice_by_number(9),
            GrantApplication.NumberOfEmployees.HAS_FEWER_THAN_10
        )
        self.assertEqual(
            GrantApplication.NumberOfEmployees.get_choice_by_number(10),
            GrantApplication.NumberOfEmployees.HAS_10_TO_49
        )
        self.assertEqual(
            GrantApplication.NumberOfEmployees.get_choice_by_number(200),
            GrantApplication.NumberOfEmployees.HAS_50_TO_249
        )
        self.assertEqual(
            GrantApplication.NumberOfEmployees.get_choice_by_number(1000),
            GrantApplication.NumberOfEmployees.HAS_250_OR_MORE
        )