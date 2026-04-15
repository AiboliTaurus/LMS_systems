from rest_framework import serializers
from .models import User, Payment


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели пользователя
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone', 'city', 'avatar', 'date_joined']
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


# Расширенный сериализатор пользователя с историей платежей
class UserWithPaymentsSerializer(UserSerializer):
    """
    Сериализатор пользователя с историей платежей
    """
    payments = PaymentSerializer(many=True, read_only=True)
    total_spent = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['payments', 'total_spent']

    def get_total_spent(self, obj):
        """Вычисляем общую сумму всех платежей пользователя"""
        return sum(payment.amount for payment in obj.payments.all())
