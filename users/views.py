from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Payment
from .serializers import UserSerializer, PaymentSerializer, UserWithPaymentsSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet для редактирования профиля пользователя
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        # для детального просмотра используем расширенный сериализатор
        if self.action == 'retrieve':
            return UserWithPaymentsSerializer
        return UserSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операций с платежами
    Задание 4: Добавлена фильтрация и сортировка
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']  # Сортировка по умолчанию: новые сверху
    filterset_fields = {
        'course': ['exact', 'isnull'],
        'lesson': ['exact', 'isnull'],
        'payment_method': ['exact'],
    }
