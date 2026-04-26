from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from users.models import User
from lms.models import Course


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными (курсы, уроки, пользователи, платежи)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🚀 Начинаем заполнение базы данных...'))

        # ==================== 1. СОЗДАНИЕ КУРСОВ ====================
        self.stdout.write(self.style.WARNING('\n📚 Создание курсов...'))

        # Проверяем наличие администратора (просто проверка, значение не нужно)
        if User.objects.filter(email='prokopjev.stenka@yandex.ru').exists():
            self.stdout.write(self.style.SUCCESS('  ✅ Администратор найден в системе'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️ Администратор не найден'))

        # Создаём тестовых пользователей
        user1, _ = User.objects.get_or_create(
            username='ivan_petrov',
            defaults={
                'email': 'ivan@example.com',
                'password': make_password('user123'),
                'first_name': 'Иван',
                'last_name': 'Петров',
                'phone': '+79990000002',
                'city': 'Санкт-Петербург'
            }
        )
        self.stdout.write(self.style.SUCCESS(f'  ✅ Пользователь: {user1.email}'))

        user2, _ = User.objects.get_or_create(
            username='maria_s',
            defaults={
                'email': 'maria@example.com',
                'password': make_password('user123'),
                'first_name': 'Мария',
                'last_name': 'Сидорова',
                'phone': '+79990000003',
                'city': 'Новосибирск'
            }
        )
        self.stdout.write(self.style.SUCCESS(f'  ✅ Пользователь: {user2.email}'))

        # Создаём курсы с привязкой к владельцам
        course1, _ = Course.objects.get_or_create(
            title='Python Basic',
            defaults={
                'description': 'Изучение основ программирования на Python. Курс для начинающих.',
                'owner': user1
            }
        )
        self.stdout.write(self.style.SUCCESS(f'  ✅ Курс: {course1.title} (владелец: {user1.email})'))

        course2, _ = Course.objects.get_or_create(
            title='Django Advanced',
            defaults={
                'description': 'Продвинутый курс по Django REST Framework и разработке API.',
                'owner': user2
            }
        )
        self.stdout.write(self.style.SUCCESS(f'  ✅ Курс: {course2.title} (владелец: {user2.email})'))

        self.stdout.write(self.style.SUCCESS('\n🎉 БАЗА ДАННЫХ УСПЕШНО ЗАПОЛНЕНА!'))
