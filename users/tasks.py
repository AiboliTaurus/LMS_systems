from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def send_payment_success_email(user_id, payment_id, amount, course_title):
    """
    Задача для отправки письма об успешной оплате.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return f"User {user_id} not found"

    subject = f"Подтверждение оплаты курса {course_title}"
    message = f"""
    Здравствуйте, {user.get_full_name() or user.email}!

    Оплата курса "{course_title}" прошла успешно.
    Сумма: {amount} ₽
    Номер платежа: {payment_id}

    Спасибо за покупку!

    С уважением,
    Команда LMS
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return f"Payment confirmation email sent to {user.email}"
    except Exception as e:
        return f"Error sending email: {e}"


@shared_task
def block_inactive_users():
    """
    Задача для блокировки неактивных пользователей.
    Блокирует пользователей, которые не заходили более месяца.
    Запускается периодически через celery-beat.
    """
    # Вычисляем дату месяц назад
    one_month_ago = timezone.now() - timedelta(days=30)

    # Находим пользователей, которые не заходили более месяца и активны
    inactive_users = User.objects.filter(
        last_login__lt=one_month_ago,
        is_active=True
    )

    # Обновляем статус (batch update)
    count = inactive_users.update(is_active=False)

    return f"Deactivated {count} inactive users who haven't logged in for more than a month"
