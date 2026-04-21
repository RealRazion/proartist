"""
Standardisierte Pagination für alle API ViewSets
"""

from rest_framework.pagination import PageNumberPagination, CursorPagination


class OptimizedPagePagination(PageNumberPagination):
    """
    Standard Seiten-basierte Pagination für kleinere bis mittlere Datasets
    """
    page_size = 50
    page_size_query_param = 'page_size'
    page_size_query_description = 'Number of results to return per page.'
    max_page_size = 200
    page_query_param = 'page'
    page_query_description = 'A page number within the paginated result set.'


class OptimizedCursorPagination(CursorPagination):
    """
    Cursor-basierte Pagination für große Datasets
    Besser für Performance bei vielen Datensätzen
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
    cursor_query_param = 'cursor'
    cursor_query_description = 'The pagination cursor value.'
    ordering = '-id'  # Default Ordering


class PaginationMixin:
    """
    Mixin für ViewSets, um standardisierte Pagination zu nutzen
    
    Beispiel:
        class TaskViewSet(PaginationMixin, viewsets.ModelViewSet):
            queryset = Task.objects.all()
            serializer_class = TaskSerializer
    """
    pagination_class = OptimizedPagePagination


class LargeDatasetPaginationMixin:
    """
    Mixin für ViewSets mit großen Datenmengen
    Nutzt Cursor-Pagination für bessere Performance
    """
    pagination_class = OptimizedCursorPagination
