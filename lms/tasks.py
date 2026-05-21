from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Course, Subscription


@shared_task
def send_course_update_notification(course_id, updated_fields):
    """
    Задача для отправки уведомлений подписчикам курса об обновлении.
    Вызывается при обновлении курса.
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return f"Course {course_id} not found"

    # Получаем всех подписчиков курса
    subscribers = Subscription.objects.filter(course=course).select_related('user')

    if not subscribers.exists():
        return f"No subscribers for course {course_id}"

    # Формируем сообщение
    subject = f"Обновление курса: {course.title}"
    message = f"""
    Здравствуйте!

    Курс "{course.title}" был обновлён.

    Обновлённые поля: {', '.join(updated_fields) if updated_fields else 'содержание'}

    Перейдите в свой личный кабинет для просмотра обновлений.

    С уважением,
    Команда LMS
    """

    # Отправляем письма всем подписчикам
    sent_count = 0
    for subscription in subscribers:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscription.user.email],
                fail_silently=False,
            )
            sent_count += 1
        except Exception as e:
            print(f"Error sending email to {subscription.user.email}: {e}")

    return f"Sent {sent_count} notifications for course {course_id}"
