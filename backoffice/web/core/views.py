from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework.pagination import PageNumberPagination


class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            return super().get(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('viewflow:index'))


class TAPPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_page_size(self, request):
        if 'page' not in request.query_params:
            return None
        return super().get_page_size(request)

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data['total_pages'] = self.page.paginator.num_pages
        return response
