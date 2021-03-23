from unittest.mock import patch

from web.grant_applications.models import GrantApplication
from web.tests.factories.grant_applications import GrantApplicationFactory, CompletedGrantApplicationFactory
from web.tests.helpers import BaseTestCase


@patch('web.grant_management.flows.NotifyService')
class TestGrantApplicationModel(BaseTestCase):

    def test_new_grant_application_sent_for_review_is_false(self, *mocks):
        ga = GrantApplicationFactory()
        self.assertFalse(ga.sent_for_review)

    def test_send_for_review_starts_flow_process(self, *mocks):
        ga = CompletedGrantApplicationFactory()
        ga.send_for_review()
        self.assertTrue(hasattr(ga, 'grant_management_process'))
        self.assertTrue(ga.sent_for_review)

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

    def test_new_grant_application_is_eligible(self, *mocks):
        ga = CompletedGrantApplicationFactory()
        self.assertTrue(ga.is_eligible)

    def test_grant_application_is_not_eligible_with_6_previous_applications(self, *mocks):
        ga = CompletedGrantApplicationFactory(previous_applications=6)
        self.assertFalse(ga.is_eligible)

    def test_grant_application_is_not_eligible_if_already_committed(self, *mocks):
        ga = CompletedGrantApplicationFactory(is_already_committed_to_event=True)
        self.assertFalse(ga.is_eligible)

    def test_grant_application_is_not_eligible_with_number_of_employees(self, *mocks):
        ga = CompletedGrantApplicationFactory(
            number_of_employees=GrantApplication.NumberOfEmployees.HAS_250_OR_MORE
        )
        self.assertFalse(ga.is_eligible)

    def test_grant_application_is_not_eligible_with_high_turnover(self, *mocks):
        ga = CompletedGrantApplicationFactory(is_turnover_greater_than=True)
        self.assertFalse(ga.is_eligible)
