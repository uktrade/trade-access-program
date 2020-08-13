from unittest.mock import patch

from web.tests.factories.grant_applications import GrantApplicationFactory
from web.tests.helpers import BaseTestCase


@patch('web.grant_management.flows.NotifyService')
class TestGrantApplicationModel(BaseTestCase):

    def test_send_for_review_starts_flow_process(self, *mocks):
        ga = GrantApplicationFactory()
        ga.send_for_review()
        self.assertTrue(hasattr(ga, 'grant_application_process'))
