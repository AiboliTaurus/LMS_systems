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

    Для тестирования оплаты используйте тестовые карты Stripe:
    - Visa: 4242 4242 4242 4242
    - Mastercard: 5555 5555 5555 4444
    - American Express: 3782 8224 6310 005
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True, default=None)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True, default=None)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_email', 'payment_date',
            'course', 'course_title', 'lesson', 'lesson_title',
            'amount', 'payment_method', 'payment_method_display',
            'status', 'status_display', 'payment_url', 'stripe_session_id'
        ]
        read_only_fields = ['id', 'payment_date', 'payment_url', 'stripe_session_id', 'status']


class CreatePaymentSerializer(serializers.Serializer):
    """
    Сериализатор для создания платежа через Stripe
    """
    course_id = serializers.IntegerField(required=False, allow_null=True)
    lesson_id = serializers.IntegerField(required=False, allow_null=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)

    def validate(self, data):
        course_id = data.get('course_id')
        lesson_id = data.get('lesson_id')

        if not course_id and not lesson_id:
            raise serializers.ValidationError("Должен быть указан course_id или lesson_id")

        if course_id and lesson_id:
            raise serializers.ValidationError("Нельзя указать одновременно course_id и lesson_id")

        return data


class PaymentStatusSerializer(serializers.ModelSerializer):
    """
    Сериализатор для статуса платежа
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_url = serializers.URLField(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'status', 'status_display', 'amount', 'payment_url']


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
        return sum(payment.amount for payment in obj.payments.filter(status='paid'))
