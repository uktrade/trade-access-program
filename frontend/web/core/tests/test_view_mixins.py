from unittest.mock import MagicMock

from web.core.view_mixins import PaginationMixin
from web.tests.helpers.testcases import BaseTestCase


class TestPaginationMixin(BaseTestCase):

    def setUp(self):
        self.mixin = PaginationMixin()
        self.mixin.get_current_page = MagicMock(return_value=1)
        self.mixin.get_pagination_total_pages = MagicMock(return_value=1)

    def test_1_page_gives_no_pagination(self):
        self.assertIsNone(self.mixin.get_pagination())

    def test_2_to_6_pages_pagination_length(self):
        for total_pages in range(2, 7):
            self.mixin.get_pagination_total_pages.return_value = total_pages
            pagination = self.mixin.get_pagination()
            self.assertEqual(len(pagination['pages']), total_pages)

    def test_2_to_6_pages_current_page(self):
        self.mixin.get_current_page.return_value = 2
        self.mixin.get_pagination_total_pages.return_value = 3
        pagination = self.mixin.get_pagination()
        self.assertIn('active', pagination['pages'][1]['class'])
        self.assertEqual(pagination['pages'][1]['text'], 2)

    def test_2_to_6_pages(self):
        self.mixin.get_current_page.return_value = 2
        self.mixin.get_pagination_total_pages.return_value = 6
        pagination = self.mixin.get_pagination()
        self.assertEqual(pagination['pages'][0]['page'], 1)
        self.assertEqual(pagination['pages'][1]['text'], 2)
        self.assertEqual(pagination['pages'][2]['page'], 3)
        self.assertEqual(pagination['pages'][3]['page'], 4)
        self.assertEqual(pagination['pages'][4]['page'], 5)
        self.assertEqual(pagination['pages'][5]['page'], 6)

    def test_7_plus_pages(self):
        self.mixin.get_current_page.return_value = 5
        self.mixin.get_pagination_total_pages.return_value = 7
        pagination = self.mixin.get_pagination()
        self.assertEqual(pagination['pages'][0]['page'], 1)
        self.assertEqual(pagination['pages'][1]['text'], self.mixin.ellipsis)
        self.assertEqual(pagination['pages'][2]['page'], 4)
        self.assertEqual(pagination['pages'][3]['text'], 5)
        self.assertEqual(pagination['pages'][4]['page'], 6)
        self.assertEqual(pagination['pages'][5]['text'], self.mixin.ellipsis)

    def test_7_plus_pages_pagination_length(self):
        self.mixin.get_pagination_total_pages.return_value = 10
        pagination = self.mixin.get_pagination()
        self.assertEqual(len(pagination['pages']), 5)

    def test_7_plus_pages_always_starts_at_page_1(self):
        self.mixin.get_pagination_total_pages.return_value = 7
        pagination = self.mixin.get_pagination()
        self.assertEqual(pagination['pages'][0]['text'], 1)

    def test_7_plus_pages_gives_starting_ellipsis(self):
        self.mixin.get_current_page.return_value = 4
        self.mixin.get_pagination_total_pages.return_value = 7
        pagination = self.mixin.get_pagination()
        self.assertEqual(
            pagination['pages'][1]['text'],
            self.mixin.ellipsis
        )

    def test_7_plus_pages_gives_ending_ellipsis(self):
        self.mixin.get_pagination_total_pages.return_value = 7
        pagination = self.mixin.get_pagination()
        self.assertEqual(
            pagination['pages'][-1]['text'],
            self.mixin.ellipsis
        )

    def test_7_plus_pages_current_page(self):
        self.mixin.get_current_page.return_value = 5
        self.mixin.get_pagination_total_pages.return_value = 10
        pagination = self.mixin.get_pagination()
        self.assertIn('active', pagination['pages'][3]['class'])
        self.assertEqual(pagination['pages'][3]['text'], 5)

    def test_7_plus_pages_current_page_2(self):
        self.mixin.get_current_page.return_value = 2
        self.mixin.get_pagination_total_pages.return_value = 10
        pagination = self.mixin.get_pagination()
        self.assertIn('active', pagination['pages'][1]['class'])
        self.assertEqual(pagination['pages'][1]['text'], 2)

    def test_7_plus_pages_current_page_is_last_page(self):
        self.mixin.get_current_page.return_value = 10
        self.mixin.get_pagination_total_pages.return_value = 10
        pagination = self.mixin.get_pagination()
        self.assertIn('active', pagination['pages'][-1]['class'])
        self.assertEqual(pagination['pages'][-1]['text'], 10)

    def test_get_current_page_defaults_to_1_if_page_is_not_specified(self):
        mixin = PaginationMixin()
        mixin.request = MagicMock()
        mixin.request.GET = {}
        self.assertEqual(mixin.get_current_page(), 1)

    def test_get_current_page_defaults_to_1_if_page_is_not_int(self):
        mixin = PaginationMixin()
        mixin.request = MagicMock()
        mixin.request.GET = {'page': 'bad-value'}
        self.assertEqual(mixin.get_current_page(), 1)
