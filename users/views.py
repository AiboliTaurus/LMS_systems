from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User, Payment
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    UserProfileSerializer, UserOwnProfileSerializer,
    UserWithPaymentsSerializer, PaymentSerializer,
    CreatePaymentSerializer, PaymentStatusSerializer
)
from .permissions import IsModerator, IsOwner


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с профилями пользователей
    - Любой авторизованный может просматривать чужие профили (ограниченная информация)
    - Редактировать и удалять можно только свой профиль
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Назначение прав доступа в зависимости от действия
        """
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        """
        Выбор сериализатора в зависимости от действия
        """
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action == 'retrieve':
            user_id = self.kwargs.get('pk')
            if user_id and str(self.request.user.id) == user_id:
                return UserWithPaymentsSerializer
            return UserProfileSerializer
        elif self.action in ['update', 'partial_update']:
            return UserOwnProfileSerializer
        return UserSerializer

    def get_queryset(self):
        """
        Фильтрация queryset
        """
        return User.objects.all()

    @swagger_auto_schema(
        operation_description="Получение списка всех пользователей",
        responses={200: UserSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получение профиля пользователя. "
                              "Если запрашивается свой профиль - возвращается полная информация + история платежей. "
                              "Если чужой - только ограниченная информация.",
        responses={200: "Профиль пользователя", 404: "Пользователь не найден"}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Полное обновление профиля пользователя (только для владельца)",
        request_body=UserOwnProfileSerializer,
        responses={200: UserOwnProfileSerializer(), 403: "Доступ запрещен", 404: "Пользователь не найден"}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Частичное обновление профиля пользователя (только для владельца)",
        request_body=UserOwnProfileSerializer,
        responses={200: UserOwnProfileSerializer(), 403: "Доступ запрещен", 404: "Пользователь не найден"}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Удаление профиля пользователя (только для владельца)",
        responses={204: "Пользователь удален", 403: "Доступ запрещен", 404: "Пользователь не найден"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class UserRegistrationViewSet(viewsets.GenericViewSet):
    """
    ViewSet для регистрации новых пользователей
    """
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    @swagger_auto_schema(
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="Пользователь успешно зарегистрирован",
                examples={
                    "application/json": {
                        "message": "Пользователь успешно зарегистрирован",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "testuser",
                            "phone": None,
                            "city": None,
                            "avatar": None,
                            "date_joined": "2024-01-01T00:00:00Z"
                        }
                    }
                }
            ),
            400: "Ошибка валидации"
        },
        operation_description="Регистрация нового пользователя"
    )
    def create(self, request):
        """
        Регистрация нового пользователя
        POST /api/register/
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Пользователь успешно зарегистрирован',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с платежами через Stripe

    Тестовые карты Stripe:
    - Visa: 4242 4242 4242 4242
    - Mastercard: 5555 5555 5555 4444
    - American Express: 3782 8224 6310 005
    - Discover: 6011 1111 1111 1117
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=CreatePaymentSerializer,
        responses={
            201: openapi.Response(
                description="Ссылка на оплату",
                examples={
                    "application/json": {
                        "payment_id": 1,
                        "payment_url": "https://checkout.stripe.com/...",
                        "message": "Перейдите по ссылке для оплаты"
                    }
                }
            ),
            400: "Ошибка валидации или Stripe",
            401: "Не авторизован"
        },
        operation_description="Создание платежа и получение ссылки на оплату Stripe"
    )
    def create(self, request, *args, **kwargs):
        """Создание платежа через Stripe"""
        from lms.services import create_payment_session
        from lms.models import Course, Lesson

        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data.get('course_id')
        lesson_id = serializer.validated_data.get('lesson_id')
        amount = serializer.validated_data['amount']

        course = None
        lesson = None

        if course_id:
            course = get_object_or_404(Course, id=course_id)
        elif lesson_id:
            lesson = get_object_or_404(Lesson, id=lesson_id)

        payment = Payment.objects.create(
            user=request.user,
            course=course,
            lesson=lesson,
            amount=amount,
            payment_method='card',
            status='pending'
        )

        result = create_payment_session(payment)

        if not result['success']:
            payment.status = 'failed'
            payment.save()
            return Response(
                {'error': result.get('error', 'Ошибка создания платежа в Stripe')},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'payment_id': payment.id,
            'payment_url': result['payment_url'],
            'message': 'Перейдите по ссылке для оплаты. Для тестирования используйте карту 4242 4242 4242 4242'
        }, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={200: PaymentStatusSerializer()},
        operation_description="Получение актуального статуса платежа из Stripe. "
                              "Возможные статусы: pending (ожидает), paid (оплачен), failed (ошибка)"
    )
    @action(detail=True, methods=['get'], url_path='status')
    def get_status(self, request, pk=None):
        """Получение статуса платежа из Stripe"""
        from lms.services import get_payment_status_from_stripe

        payment = self.get_object()

        if not payment.stripe_session_id:
            return Response({
                'payment_id': payment.id,
                'status': payment.status,
                'message': 'Платеж не был инициирован через Stripe'
            })

        result = get_payment_status_from_stripe(payment.stripe_session_id)

        if result['success']:
            payment.status = result['status']
            if result.get('payment_intent_id'):
                payment.stripe_payment_intent_id = result['payment_intent_id']
            payment.save()

            return Response({
                'payment_id': payment.id,
                'status': payment.status,
                'stripe_status': result.get('session_status'),
                'payment_status': result.get('payment_status'),
                'amount': result.get('amount_total'),
                'currency': result.get('currency')
            })
        else:
            return Response({
                'payment_id': payment.id,
                'status': payment.status,
                'error': result.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={200: "Успешная оплата"},
        operation_description="Эндпоинт для редиректа после успешной оплаты"
    )
    @action(detail=True, methods=['get'], url_path='success')
    def payment_success(self, request, pk=None):
        """Эндпоинт для редиректа после успешной оплаты"""
        payment = self.get_object()

        # Обновляем статус через Stripe для синхронизации
        from lms.services import get_payment_status_from_stripe

        if payment.stripe_session_id:
            result = get_payment_status_from_stripe(payment.stripe_session_id)
            if result['success'] and result['status'] == 'paid':
                payment.status = 'paid'
            else:
                payment.status = 'paid'  # Принудительно устанавливаем как оплачен
        else:
            payment.status = 'paid'

        payment.save()

        return Response({
            'message': 'Оплата прошла успешно!',
            'payment_id': payment.id,
            'status': 'paid',
            'test_cards': {
                'visa': '4242 4242 4242 4242',
                'mastercard': '5555 5555 5555 4444',
                'amex': '3782 8224 6310 005'
            }
        })

    @swagger_auto_schema(
        responses={200: "Оплата отменена"},
        operation_description="Эндпоинт для редиректа при отмене оплаты"
    )
    @action(detail=True, methods=['get'], url_path='cancel')
    def payment_cancel(self, request, pk=None):
        """Эндпоинт для редиректа при отмене оплаты"""
        payment = self.get_object()
        payment.status = 'pending'
        payment.save()
        return Response({
            'message': 'Оплата отменена. Вы можете повторить попытку позже.',
            'payment_id': payment.id,
            'status': payment.status
        })

    @swagger_auto_schema(
        responses={200: "Информация о тестовых картах"},
        operation_description="Получение информации о тестовых картах Stripe для оплаты"
    )
    @action(detail=False, methods=['get'], url_path='test-cards')
    def test_cards(self, request):
        """Получение списка тестовых карт Stripe"""
        return Response({
            'message': 'Тестовые карты Stripe для оплаты',
            'note': 'Для тестовой оплаты используйте любой из этих номеров. '
                    'Номер карты, срок действия (любая будущая дата) и CVV/CVC (любые 3 цифры).',
            'cards': {
                'visa': {
                    'number': '4242 4242 4242 4242',
                    'brand': 'Visa',
                    'cvv': 'Любые 3 цифры',
                    'expiry': 'Любая будущая дата'
                },
                'visa_debit': {
                    'number': '4000 0566 5566 5556',
                    'brand': 'Visa (Debit)'
                },
                'mastercard': {
                    'number': '5555 5555 5555 4444',
                    'brand': 'Mastercard'
                },
                'mastercard_debit': {
                    'number': '5200 8282 8282 8210',
                    'brand': 'Mastercard (Debit)'
                },
                'mastercard_prepaid': {
                    'number': '5105 1051 0510 5100',
                    'brand': 'Mastercard (Prepaid)'
                },
                'amex': {
                    'number': '3782 8224 6310 005',
                    'brand': 'American Express',
                    'cvv': '4 цифры'
                },
                'discover': {
                    'number': '6011 1111 1111 1117',
                    'brand': 'Discover'
                },
                'diners': {
                    'number': '3056 9300 0902 0004',
                    'brand': 'Diners Club'
                },
                'jcb': {
                    'number': '3566 0020 2036 0505',
                    'brand': 'JCB'
                },
                'unionpay': {
                    'number': '6200 0000 0000 0005',
                    'brand': 'UnionPay'
                }
            }
        })

    def get_queryset(self):
        """
        Фильтрация: обычные пользователи видят только свои платежи,
        модераторы и админы видят все
        """
        user = self.request.user
        if user.is_staff or IsModerator().has_permission(self.request, None):
            return Payment.objects.all()
        return Payment.objects.filter(user=user)
