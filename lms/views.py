from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner, IsOwnerOrModerator
from .tasks import send_course_update_notification


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операций с курсами
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
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
        Фильтрация queryset:
        - Модераторы видят все курсы
        - Обычные пользователи видят только свои курсы
        """
        user = self.request.user
        if IsModerator().has_permission(self.request, None):
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        """При создании курса автоматически привязываем владельца"""
        serializer.save(owner=self.request.user)

    @swagger_auto_schema(
        operation_description="Получение списка всех курсов с пагинацией",
        responses={200: CourseSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создание нового курса (только для обычных пользователей, не модераторов)",
        request_body=CourseSerializer,
        responses={201: CourseSerializer(), 403: "Доступ запрещен"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получение детальной информации о курсе (включая список уроков и is_subscribed)",
        responses={200: CourseSerializer(), 404: "Курс не найден"}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Полное обновление курса (только владелец или модератор)",
        request_body=CourseSerializer,
        responses={200: CourseSerializer(), 403: "Доступ запрещен", 404: "Курс не найден"}
    )
    def update(self, request, *args, **kwargs):
        """
        Полное обновление курса с отправкой уведомлений подписчикам.
        Дополнительное задание: проверка на 4 часа.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Сохраняем старые данные для сравнения
        old_title = instance.title
        old_description = instance.description
        old_updated_at = instance.updated_at

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Определяем, какие поля были обновлены
        updated_fields = []
        if instance.title != old_title:
            updated_fields.append('название')
        if instance.description != old_description:
            updated_fields.append('описание')

        # Дополнительное задание: проверка на 4 часа
        now = timezone.now()
        hours_since_update = (now - old_updated_at).total_seconds() / 3600

        # Отправляем уведомления, только если курс не обновлялся более 4 часов
        if updated_fields and hours_since_update >= 4:
            send_course_update_notification.delay(instance.id, updated_fields)
        elif updated_fields:
            print(f"Course {instance.id} updated, but last update was {hours_since_update:.1f} hours ago. Notification not sent.")

        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Частичное обновление курса (только владелец или модератор)",
        request_body=CourseSerializer,
        responses={200: CourseSerializer(), 403: "Доступ запрещен", 404: "Курс не найден"}
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Частичное обновление курса с отправкой уведомлений подписчикам.
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Удаление курса (только владелец)",
        responses={204: "Курс удален", 403: "Доступ запрещен", 404: "Курс не найден"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """
    Generic-класс для получения списка уроков и создания нового урока
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
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        else:
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
        """При создании урока автоматически привязываем владельца"""
        serializer.save(owner=self.request.user)

    @swagger_auto_schema(
        operation_description="Получение списка всех уроков с фильтрацией, поиском и пагинацией",
        responses={200: LessonSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создание нового урока (только для обычных пользователей, не модераторов). "
                              "Ссылка на видео должна быть с youtube.com или youtu.be",
        request_body=LessonSerializer,
        responses={201: LessonSerializer(), 400: "Ошибка валидации", 403: "Доступ запрещен"}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Generic-класс для получения, обновления и удаления конкретного урока
    """
    serializer_class = LessonSerializer

    def get_permissions(self):
        """
        Назначение прав доступа в зависимости от метода запроса
        """
        if self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
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

    @swagger_auto_schema(
        operation_description="Получение детальной информации об уроке",
        responses={200: LessonSerializer(), 404: "Урок не найден"}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Полное обновление урока (только владелец или модератор)",
        request_body=LessonSerializer,
        responses={200: LessonSerializer(), 403: "Доступ запрещен", 404: "Урок не найден"}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Частичное обновление урока (только владелец или модератор)",
        request_body=LessonSerializer,
        responses={200: LessonSerializer(), 403: "Доступ запрещен", 404: "Урок не найден"}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Удаление урока (только владелец)",
        responses={204: "Урок удален", 403: "Доступ запрещен", 404: "Урок не найден"}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class SubscriptionAPIView(APIView):
    """
    APIView для управления подпиской на курс
    POST /api/subscribe/ - создание или удаление подписки
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'course_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID курса'
                ),
            },
            required=['course_id']
        ),
        responses={
            200: openapi.Response(
                description="Результат подписки",
                examples={
                    "application/json": {
                        "message": "Подписка добавлена",
                        "subscribed": True,
                        "course_id": 1,
                        "course_title": "Python Basic"
                    }
                }
            ),
            400: "Не указан ID курса",
            404: "Курс не найден"
        },
        operation_description="Создание или удаление подписки на курс"
    )
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
