from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner, IsOwnerOrModerator


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операций с курсами
    Права доступа:
    - Создание: только обычные пользователи (НЕ модераторы)
    - Просмотр: все авторизованные
    - Редактирование: владелец ИЛИ модератор
    - Удаление: только владелец (модераторы НЕ могут удалять)
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'id']
    filterset_fields = ['title']

    def get_permissions(self):
        """
        Назначение прав доступа в зависимости от действия
        """
        if self.action == 'create':
            # Создание: только обычные пользователи (не модераторы)
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['update', 'partial_update']:
            # Редактирование: владелец ИЛИ модератор
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action == 'destroy':
            # Удаление: только владелец (модераторы НЕ могут удалять)
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            # Просмотр: все авторизованные пользователи
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        """
        Фильтрация queryset:
        - Модераторы видят все курсы
        - Обычные пользователи видят только свои курсы
        """
        user = self.request.user
        if IsModerator().has_permission(self.request, None):
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        """
        При создании курса автоматически привязываем владельца
        """
        serializer.save(owner=self.request.user)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """
    Generic-класс для получения списка уроков и создания нового урока
    Права доступа:
    - Просмотр: все авторизованные
    - Создание: только обычные пользователи (НЕ модераторы)
    """
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'course__title']
    filterset_fields = ['course']

    def get_permissions(self):
        """
        Назначение прав доступа в зависимости от метода запроса
        """
        if self.request.method == 'POST':
            # Создание: только обычные пользователи (не модераторы)
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        else:
            # Просмотр: все авторизованные
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        """
        Фильтрация queryset:
        - Модераторы видят все уроки
        - Обычные пользователи видят только свои уроки
        """
        user = self.request.user
        if IsModerator().has_permission(self.request, None):
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        """
        При создании урока автоматически привязываем владельца
        """
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Generic-класс для получения, обновления и удаления конкретного урока
    Права доступа:
    - Просмотр: все авторизованные
    - Редактирование: владелец ИЛИ модератор
    - Удаление: только владелец (модераторы НЕ могут удалять)
    """
    serializer_class = LessonSerializer

    def get_permissions(self):
        """
        Назначение прав доступа в зависимости от метода запроса
        """
        if self.request.method in ['PUT', 'PATCH']:
            # Редактирование: владелец ИЛИ модератор
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.request.method == 'DELETE':
            # Удаление: только владелец
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            # Просмотр: все авторизованные
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        """
        Фильтрация queryset:
        - Модераторы видят все уроки
        - Обычные пользователи видят только свои уроки
        """
        user = self.request.user
        if IsModerator().has_permission(self.request, None):
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)
