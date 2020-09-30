from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class PageContextMixin:
    page = {}

    def get_context_data(self, **kwargs):
        kwargs['page'] = self.page
        return super().get_context_data(**kwargs)


class BackContextMixin:
    back_text = None
    back_url = '#'

    def get_context_data(self, **kwargs):
        back_url = self.back_url
        if hasattr(self, 'get_back_url'):
            back_url = self.get_back_url()
        elif hasattr(self, 'back_url_name') and self.object:
            back_url = reverse(self.back_url_name, kwargs={'pk': self.object.pk})
        elif hasattr(self, 'back_url_name'):
            back_url = reverse(self.back_url_name)

        kwargs['back'] = {
            'text': self.back_text or _('Back'),
            'url': back_url
        }

        return super().get_context_data(**kwargs)


class SuccessUrlObjectPkMixin:

    def get_success_url(self):
        return reverse(self.success_url_name, kwargs={'pk': self.object.pk})
