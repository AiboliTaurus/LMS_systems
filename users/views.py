from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet для редактирования профиля пользователя
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        # Для безопасности: пользователь может видеть только свой профиль
        # но по заданию пока без авторизации, так что оставляем все
        return User.objects.all()
