from web.grant_management.models import GrantManagementProcess
from web.tests.factories.grant_management import GrantManagementProcessFactory
from web.tests.helpers import BaseTestCase


class TestGrantManagementProcessModel(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.gm_process = GrantManagementProcessFactory()

    def test_is_approved(self):
        self.assertFalse(self.gm_process.is_approved)
        self.gm_process.decision = GrantManagementProcess.Decision.APPROVED
        self.gm_process.save()
        self.assertTrue(self.gm_process.is_approved)

    def test_is_rejected(self):
        self.assertFalse(self.gm_process.is_rejected)
        self.gm_process.decision = GrantManagementProcess.Decision.REJECTED
        self.gm_process.save()
        self.assertTrue(self.gm_process.is_rejected)
