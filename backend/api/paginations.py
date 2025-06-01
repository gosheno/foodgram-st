from django.core.cache import cache
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'

    def paginate_queryset(self, queryset, request, view=None):
        cache_key = f"paginated_{request.path}_{request.query_params}"
        cached_data = cache.get(cache_key)
        if cached_data:
            self.page = cached_data['page']
            self.request = request
            return self.page.object_list
        page = super().paginate_queryset(queryset, request, view)
        if page is not None:
            cache.set(cache_key, {
                'page': self.page,
            }, timeout=60 * 5)
        return page

    def get_paginated_response(self, data):
        if not hasattr(self, 'page'):
            return super().get_paginated_response(data)
        return super().get_paginated_response(data)
