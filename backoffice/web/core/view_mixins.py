from django.urls import reverse


class PageContextMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = self.page
        return context


class SuccessUrlObjectPkMixin:

    def get_success_url(self):
        return reverse(self.success_url_name, kwargs={'pk': self.object.pk})
