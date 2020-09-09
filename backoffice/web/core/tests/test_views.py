from web.tests.helpers import BaseTestCase


class TestErrorViews(BaseTestCase):

    def test_404(self):
        response = self.client.get('/not-a-valid-path/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
