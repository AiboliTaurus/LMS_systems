from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from .paginators import CoursePaginator, LessonPaginator
from users.permissions import IsModerator, IsOwner, IsOwnerOrModerator


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операций с курсами
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator  # Добавляем пагинацию
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'id']
    filterset_fields = ['title']

    def get_serializer_context(self):
        """
        Передаём request в контекст сериализатора для определения подписки
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_permissions(self):
        """
        Назначение прав доступа в зависимости от действия
        """
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        """
        Фильтрация queryset
        """
        user = self.request.user
        if IsModerator().has_permission(self.request, None):
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """
    Generic-класс для получения списка уроков и создания нового урока
    """
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator  # Добавляем пагинацию
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'course__title']
    filterset_fields = ['course']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if IsModerator().has_permission(self.request, None):
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Generic-класс для получения, обновления и удаления конкретного урока
    """
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if IsModerator().has_permission(self.request, None):
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class SubscriptionAPIView(APIView):
    """
    APIView для управления подпиской на курс
    POST /api/subscribe/ - создание или удаление подписки
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Создание или удаление подписки
        Ожидает: {"course_id": 1}
        """
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {'error': 'Не указан ID курса'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем курс или возвращаем 404
        course = get_object_or_404(Course, id=course_id)
        user = request.user

        # Проверяем, есть ли уже подписка
        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            # Если есть - удаляем
            subscription.delete()
            message = 'Подписка удалена'
            subscribed = False
        else:
            # Если нет - создаём
            Subscription.objects.create(user=user, course=course)
            message = 'Подписка добавлена'
            subscribed = True

        return Response({
            'message': message,
            'subscribed': subscribed,
            'course_id': course.id,
            'course_title': course.title
        }, status=status.HTTP_200_OK)
