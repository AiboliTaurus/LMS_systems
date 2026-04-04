from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели пользователя
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone', 'city', 'avatar', 'date_joined']
        read_only_fields = ['id', 'date_joined']
