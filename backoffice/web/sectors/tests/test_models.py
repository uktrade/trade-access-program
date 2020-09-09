from rest_framework.exceptions import ValidationError

from web.tests.factories.sector import SectorFactory
from web.tests.helpers import BaseTestCase


class TestSectorModel(BaseTestCase):

    def test_sector_code_validator(self, *mocks):
        self.assertRaises(ValidationError, SectorFactory(sector_code='Bad001').full_clean)
