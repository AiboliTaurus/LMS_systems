from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Payment


class UserSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для модели пользователя
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone', 'city', 'avatar', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'password2', 'phone', 'city', 'avatar']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate(self, attrs):
        """Проверка совпадения паролей"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        """Создание пользователя с хэшированием пароля"""
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(UserSerializer):
    """
    Сериализатор для просмотра чужого профиля (ограниченная информация)
    """
    class Meta(UserSerializer.Meta):
        fields = ['id', 'email', 'username', 'city', 'avatar', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserOwnProfileSerializer(UserSerializer):
    """
    Сериализатор для просмотра/редактирования СВОЕГО профиля (полная информация)
    """
    class Meta(UserSerializer.Meta):
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели платежа
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True, default=None)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True, default=None)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_email', 'payment_date',
            'course', 'course_title', 'lesson', 'lesson_title',
            'amount', 'payment_method', 'payment_method_display'
        ]
        read_only_fields = ['id', 'payment_date']


# Дополнительное задание: Расширенный сериализатор пользователя с историей платежей
class UserWithPaymentsSerializer(UserOwnProfileSerializer):
    """
    Сериализатор пользователя с историей платежей (только для СВОЕГО профиля)
    """
    payments = PaymentSerializer(many=True, read_only=True)
    total_spent = serializers.SerializerMethodField()

    class Meta(UserOwnProfileSerializer.Meta):
        fields = UserOwnProfileSerializer.Meta.fields + ['payments', 'total_spent']

    def get_total_spent(self, obj):
        """Вычисляем общую сумму всех платежей пользователя"""
        return sum(payment.amount for payment in obj.payments.all())
