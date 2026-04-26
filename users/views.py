from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import User, Payment
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    UserProfileSerializer, UserOwnProfileSerializer,
    UserWithPaymentsSerializer, PaymentSerializer
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
            # Регистрация доступна всем
            self.permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Обновление и удаление только для владельца
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            # Просмотр для авторизованных
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        """
        Выбор сериализатора в зависимости от действия
        """
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action == 'retrieve':
            # Для просмотра профиля: проверяем, свой это профиль или чужой
            user_id = self.kwargs.get('pk')
            if user_id and str(self.request.user.id) == user_id:
                return UserWithPaymentsSerializer  # Свой профиль - полная информация + платежи
            return UserProfileSerializer  # Чужой профиль - ограниченная информация
        elif self.action in ['update', 'partial_update']:
            return UserOwnProfileSerializer  # Редактирование своего профиля
        return UserSerializer

    def get_queryset(self):
        """
        Фильтрация queryset
        """
        return User.objects.all()


class UserRegistrationViewSet(viewsets.GenericViewSet):
    """
    ViewSet для регистрации новых пользователей
    """
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

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
    ViewSet для CRUD операций с платежами
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]  # Только авторизованные

    def get_queryset(self):
        """
        Фильтрация: обычные пользователи видят только свои платежи,
        модераторы и админы видят все
        """
        user = self.request.user
        if user.is_staff or IsModerator().has_permission(self.request, None):
            return Payment.objects.all()
        return Payment.objects.filter(user=user)
