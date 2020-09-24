from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class PageContextMixin:
    page = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = self.page
        return context


class BackContextMixin:
    back_text = None
    back_url = '#'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if hasattr(self, 'get_back_url'):
            back_url = self.get_back_url()
        elif hasattr(self, 'back_url_name'):
            back_url = reverse(self.back_url_name, kwargs={'pk': self.object.pk})
        else:
            back_url = self.back_url

        context['back'] = {
            'text': self.back_text or _('Back'),
            'url': back_url
        }

        return context


class SuccessUrlObjectPkMixin:

    def get_success_url(self):
        return reverse(self.success_url_name, kwargs={'pk': self.object.pk})
