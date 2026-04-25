from rest_framework.pagination import PageNumberPagination


class CoursePaginator(PageNumberPagination):
    """
    Пагинатор для курсов
    """
    page_size = 5  # Количество элементов на странице
    page_size_query_param = 'page_size'  # Параметр для изменения количества элементов
    max_page_size = 20  # Максимальное количество элементов на странице


class LessonPaginator(PageNumberPagination):
    """
    Пагинатор для уроков
    """
    page_size = 10  # Количество элементов на странице
    page_size_query_param = 'page_size'  # Параметр для изменения количества элементов
    max_page_size = 50  # Максимальное количество элементов на странице
