from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination


def handler404(request, exception):
    return render(request, 'core/404.html', status=404)


def handler500(request, *args, **argv):
    return render(request, 'core/500.html', status=404)


class PageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_page_size(self, request):
        if 'page' not in request.query_params:
            return None
        return super().get_page_size(request)

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data['total_pages'] = self.page.paginator.num_pages
        return response
