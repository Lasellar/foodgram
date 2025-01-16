from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageLimitPagination(PageNumberPagination):
    """
    Кастомный пагинатор для уровня проекта.
    """
    page_size_query_param = 'limit'


class PageLimitAndRecipesLimitPagination(PageNumberPagination):
    """
    Кастомный пагинатор.
    """

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
                "tags": self.request.query_params.get('tags')
            }
        )
