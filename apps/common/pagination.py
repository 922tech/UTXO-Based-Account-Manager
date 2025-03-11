from rest_framework import pagination
from rest_framework.response import Response


class LimitedLimitOffsetPagination(pagination.LimitOffsetPagination):
    default_limit = 10
    max_limit = 20


class SimplePagination(pagination.PageNumberPagination):
    page_size = 10
    max_page_size = 30
    page_size_query_param = 'page_size'
    ordering = '-id'

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'current': self.page.number,
            'last': self.page.paginator.num_pages,
            'results': data
        })
