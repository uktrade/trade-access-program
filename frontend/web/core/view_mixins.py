from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class PageContextMixin:
    page = {}

    def get_context_data(self, **kwargs):
        kwargs['page'] = self.page
        return super().get_context_data(**kwargs)


class BackContextMixin:
    back_text = None
    back_url = None

    def get_context_data(self, **kwargs):
        if hasattr(self, 'get_back_url'):
            self.back_url = self.get_back_url()
        elif hasattr(self, 'back_url_name') and self.object:
            self.back_url = reverse(self.back_url_name, kwargs={'pk': self.object.pk})
        elif hasattr(self, 'back_url_name'):
            self.back_url = reverse(self.back_url_name)

        if self.back_url:
            kwargs['back'] = {
                'text': self.back_text or _('Back'),
                'url': self.back_url
            }

        return super().get_context_data(**kwargs)


class SuccessUrlObjectPkMixin:

    def get_success_url(self):
        return reverse(self.success_url_name, kwargs={'pk': self.object.pk})
