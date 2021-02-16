from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _


class BackContextMixin:
    back_text = None
    back_url = None

    def get_back_url(self):
        if hasattr(self, 'back_url_name') and getattr(self, 'object', None):
            return reverse(self.back_url_name, args=(self.object.pk,))
        elif hasattr(self, 'back_url_name'):
            return reverse(self.back_url_name)

    def get_context_data(self, **kwargs):
        self.back_url = self.get_back_url()

        if self.back_url:
            kwargs['back'] = {
                'text': self.back_text or _('Back'),
                'url': self.back_url
            }

        return super().get_context_data(**kwargs)


class SuccessUrlObjectPkMixin:
    success_url_name = None

    def get_success_url(self):
        if self.object.has_viewed_review_page:
            return reverse('grant-applications:application-review', args=(self.object.pk,))
        return reverse(self.success_url_name, args=(self.object.pk,))


class PaginationMixin:
    """
    Pagination data mixin for views
    """
    ellipsis = '...'

    def get_extra_pagination_href_params(self):
        return ''

    def get_current_page(self):
        try:
            return int(self.request.GET.get('page', 1))
        except ValueError:
            return 1

    def get_pagination_total_pages(self):
        raise NotImplementedError('.get_pagination_total_pages() must be overridden.')

    def get_basic_pagination_pages(self, current_page, total_pages, extra_href_params):
        pages = []
        for i in range(1, total_pages + 1):
            if i == current_page:
                pages.append({
                    'class': 'hmcts-pagination__item hmcts-pagination__item--active',
                    'text': current_page
                })
            else:
                pages.append({'href': f'?page={i}&{extra_href_params}', 'page': i})
        return pages

    def get_dotted_pagination_pages(self, current_page, total_pages, previous_page, next_page,
                                    extra_href_params):
        pages = [
            {'href': f'?page=1&{extra_href_params}', 'page': 1},
            {'href': f'?page={previous_page}&{extra_href_params}', 'page': previous_page},
            {
                'class': 'hmcts-pagination__item hmcts-pagination__item--active',
                'text': current_page
            },
            {'href': f'?page={next_page}&{extra_href_params}', 'page': next_page},
        ]

        if current_page == 1:
            pages.pop(1)
            pages.pop(0)
            pages.append({'href': f'?page=3&{extra_href_params}', 'page': 3})
            pages.append({'href': f'?page=4&{extra_href_params}', 'page': 4})

        if current_page == 2:
            pages.pop(1)
            pages.append({'href': f'?page=4&{extra_href_params}', 'page': 4})

        if current_page == total_pages:
            pages.pop(-1)

        # Insert start "..."
        if current_page > 3:
            pages.insert(1, {
                'class': 'hmcts-pagination__item hmcts-pagination__item--dots',
                'text': self.ellipsis
            })

        # Insert end "..."
        if current_page <= total_pages - 2:
            pages.insert(len(pages), {
                'class': 'hmcts-pagination__item hmcts-pagination__item--dots',
                'text': self.ellipsis
            })

        return pages

    def get_pagination(self):
        """
        :return: Any of:
            - 1 page  -->  None (no pagination)
            - 6 pages or fewer  -->  Previous  1  2  3  4  5  6  Next
            - 7 pages or more
                - and current is page 1 --> Previous  1*  2  3  4  ...  Next
                - and current is page 2 --> Previous  1  2*  3  4  ...  Next
                - and current is page 3 --> Previous  1  2  3*  4  ...  Next
                - and current is somewhere in the middle --> Previous  1  ...  7  8*  9  ...  Next
                - and current is penultimate --> Previous  1  ...  7  8*  9  Next
                - and current is last --> Previous  1  ...  7  8  9*  Next
        """
        total_pages = self.get_pagination_total_pages()
        current_page = self.get_current_page()
        extra_href_params = urlencode(self.get_extra_pagination_href_params())

        if total_pages and total_pages > 1:
            pagination = {
                'previous': {
                    'page': max(current_page - 1, 1),
                    'href': f'?page={max(current_page - 1, 1)}&{extra_href_params}'
                },
                'next': {
                    'page': min(current_page + 1, total_pages),
                    'href': f'?page={min(current_page + 1, total_pages)}&{extra_href_params}'
                }
            }
            if 1 < total_pages <= 6:
                pagination['pages'] = self.get_basic_pagination_pages(
                    current_page, total_pages, extra_href_params
                )
            elif total_pages >= 7:
                pagination['pages'] = self.get_dotted_pagination_pages(
                    current_page,
                    total_pages,
                    pagination['previous']['page'],
                    pagination['next']['page'],
                    extra_href_params
                )
            return pagination

    def get_context_data(self, **kwargs):
        kwargs['pagination'] = self.get_pagination()
        return super().get_context_data(**kwargs)


class SaveStateMixin:
    success_url_name = None

    def save_state(self, form):
        application = form.instance
        application.state_url_name = self.success_url_name
        application.save()

    def form_valid(self, form):
        form_valid = super().form_valid(form)
        self.save_state(form)
        return form_valid
