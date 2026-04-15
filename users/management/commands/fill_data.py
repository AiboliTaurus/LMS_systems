from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from users.models import User, Payment
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными (курсы, уроки, пользователи, платежи)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🚀 Начинаем заполнение базы данных...'))

        # ==================== 1. СОЗДАНИЕ КУРСОВ ====================
        self.stdout.write(self.style.WARNING('\n📚 Создание курсов...'))

        course1, created1 = Course.objects.get_or_create(
            title='Python Basic',
            defaults={
                'description': 'Изучение основ программирования на Python. Курс для начинающих.',
                'preview': ''
            }
        )
        if created1:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан курс: {course1.title} (ID: {course1.id})'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Курс уже существует: {course1.title} (ID: {course1.id})'))

        course2, created2 = Course.objects.get_or_create(
            title='Django Advanced',
            defaults={
                'description': 'Продвинутый курс по Django REST Framework и разработке API.',
                'preview': ''
            }
        )
        if created2:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан курс: {course2.title} (ID: {course2.id})'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Курс уже существует: {course2.title} (ID: {course2.id})'))

        course3, created3 = Course.objects.get_or_create(
            title='PostgreSQL для разработчиков',
            defaults={
                'description': 'Изучение PostgreSQL, оптимизация запросов и работа с большими данными.',
                'preview': ''
            }
        )
        if created3:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан курс: {course3.title} (ID: {course3.id})'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Курс уже существует: {course3.title} (ID: {course3.id})'))

        # ==================== 2. СОЗДАНИЕ УРОКОВ ====================
        self.stdout.write(self.style.WARNING('\n📖 Создание уроков...'))

        # Уроки для курса Python Basic (course1)
        lesson1, created1 = Lesson.objects.get_or_create(
            title='Введение в Python',
            course=course1,
            defaults={
                'description': 'Установка Python, настройка окружения, первые шаги.',
                'video_link': 'https://www.youtube.com/watch?v=example1',
                'preview': ''
            }
        )
        if created1:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан урок: {lesson1.title} (курс: {course1.title})'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Урок уже существует: {lesson1.title}'))

        lesson2, created2 = Lesson.objects.get_or_create(
            title='Переменные и типы данных',
            course=course1,
            defaults={
                'description': 'Изучение переменных, базовых типов данных и операций с ними.',
                'video_link': 'https://www.youtube.com/watch?v=example2',
                'preview': ''
            }
        )
        if created2:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан урок: {lesson2.title} (курс: {course1.title})'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Урок уже существует: {lesson2.title}'))

        lesson3, created3 = Lesson.objects.get_or_create(
            title='Функции и модули',
            course=course1,
            defaults={
                'description': 'Создание функций, работа с модулями и библиотеками.',
                'video_link': 'https://www.youtube.com/watch?v=example3',
                'preview': ''
            }
        )
        if created3:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан урок: {lesson3.title} (курс: {course1.title})'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Урок уже существует: {lesson3.title}'))

        # Уроки для курса Django Advanced (course2)
        lesson4, created4 = Lesson.objects.get_or_create(
            title='Введение в Django',
            course=course2,
            defaults={
                'description': 'Установка Django, создание первого проекта.',
                'video_link': 'https://www.youtube.com/watch?v=example4',
                'preview': ''
            }
        )
        if created4:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан урок: {lesson4.title} (курс: {course2.title})'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Урок уже существует: {lesson4.title}'))

        lesson5, created5 = Lesson.objects.get_or_create(
            title='Django REST Framework',
            course=course2,
            defaults={
                'description': 'Создание API с помощью DRF, сериализаторы, вьюсеты.',
                'video_link': 'https://www.youtube.com/watch?v=example5',
                'preview': ''
            }
        )
        if created5:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан урок: {lesson5.title} (курс: {course2.title})'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Урок уже существует: {lesson5.title}'))

        # ==================== 3. ПРОВЕРКА АДМИНИСТРАТОРА ====================
        self.stdout.write(self.style.WARNING('\n👤 Проверка администратора...'))

        try:
            admin = User.objects.get(email='prokopjev.stenka@yandex.ru')
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Администратор найден: {admin.email}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('  ❌ Администратор с email prokopjev.stenka@yandex.ru НЕ НАЙДЕН!'))
            self.stdout.write(self.style.WARNING('  ⚠️  Пожалуйста, создайте администратора вручную:'))
            self.stdout.write('     python manage.py createsuperuser')
            admin = None

        # ==================== 4. СОЗДАНИЕ ОБЫЧНЫХ ПОЛЬЗОВАТЕЛЕЙ ====================
        self.stdout.write(self.style.WARNING('\n👥 Создание обычных пользователей...'))

        user1, created_u1 = User.objects.get_or_create(
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
        if created_u1:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан пользователь: {user1.email} (пароль: user123)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Пользователь уже существует: {user1.email}'))

        user2, created_u2 = User.objects.get_or_create(
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
        if created_u2:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан пользователь: {user2.email} (пароль: user123)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Пользователь уже существует: {user2.email}'))

        user3, created_u3 = User.objects.get_or_create(
            username='alexey_k',
            defaults={
                'email': 'alexey@example.com',
                'password': make_password('user123'),
                'first_name': 'Алексей',
                'last_name': 'Кузнецов',
                'phone': '+79990000004',
                'city': 'Екатеринбург'
            }
        )
        if created_u3:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан пользователь: {user3.email} (пароль: user123)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Пользователь уже существует: {user3.email}'))

        # ==================== 5. СОЗДАНИЕ ПЛАТЕЖЕЙ ====================
        self.stdout.write(self.style.WARNING('\n💰 Создание платежей...'))

        if admin:
            # Платежи для администратора
            payment1, created_p1 = Payment.objects.get_or_create(
                user=admin,
                course=course1,
                defaults={
                    'amount': 4999.00,
                    'payment_method': 'transfer'
                }
            )
            if created_p1:
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Платеж: {admin.email} -> курс "{course1.title}" = 4999.00 ₽'))
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'  ⚡ Платеж уже существует: {admin.email} -> курс "{course1.title}"'))

            payment2, created_p2 = Payment.objects.get_or_create(
                user=admin,
                lesson=lesson2,
                defaults={
                    'amount': 999.00,
                    'payment_method': 'cash'
                }
            )
            if created_p2:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Платеж: {admin.email} -> урок "{lesson2.title}" = 999.00 ₽'))
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'  ⚡ Платеж уже существует: {admin.email} -> урок "{lesson2.title}"'))
        else:
            self.stdout.write(self.style.ERROR('  ⚠️  Платежи для администратора не созданы (администратор не найден)'))

        # Платежи для Ивана
        payment3, created_p3 = Payment.objects.get_or_create(
            user=user1,
            course=course1,
            defaults={
                'amount': 4999.00,
                'payment_method': 'transfer'
            }
        )
        if created_p3:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Платеж: {user1.email} -> курс "{course1.title}" = 4999.00 ₽'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Платеж уже существует: {user1.email} -> курс "{course1.title}"'))

        payment4, created_p4 = Payment.objects.get_or_create(
            user=user1,
            course=course2,
            defaults={
                'amount': 7999.00,
                'payment_method': 'transfer'
            }
        )
        if created_p4:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Платеж: {user1.email} -> курс "{course2.title}" = 7999.00 ₽'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Платеж уже существует: {user1.email} -> курс "{course2.title}"'))

        payment5, created_p5 = Payment.objects.get_or_create(
            user=user1,
            lesson=lesson5,
            defaults={
                'amount': 1499.00,
                'payment_method': 'cash'
            }
        )
        if created_p5:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Платеж: {user1.email} -> урок "{lesson5.title}" = 1499.00 ₽'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Платеж уже существует: {user1.email} -> урок "{lesson5.title}"'))

        # Платежи для Марии
        payment6, created_p6 = Payment.objects.get_or_create(
            user=user2,
            course=course2,
            defaults={
                'amount': 7999.00,
                'payment_method': 'transfer'
            }
        )
        if created_p6:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Платеж: {user2.email} -> курс "{course2.title}" = 7999.00 ₽'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Платеж уже существует: {user2.email} -> курс "{course2.title}"'))

        payment7, created_p7 = Payment.objects.get_or_create(
            user=user2,
            lesson=lesson4,
            defaults={
                'amount': 999.00,
                'payment_method': 'cash'
            }
        )
        if created_p7:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Платеж: {user2.email} -> урок "{lesson4.title}" = 999.00 ₽'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Платеж уже существует: {user2.email} -> урок "{lesson4.title}"'))

        # Платежи для Алексея
        payment8, created_p8 = Payment.objects.get_or_create(
            user=user3,
            course=course3,
            defaults={
                'amount': 6999.00,
                'payment_method': 'transfer'
            }
        )
        if created_p8:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Платеж: {user3.email} -> курс "{course3.title}" = 6999.00 ₽'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Платеж уже существует: {user3.email} -> курс "{course3.title}"'))

        payment9, created_p9 = Payment.objects.get_or_create(
            user=user3,
            course=course1,
            defaults={
                'amount': 4999.00,
                'payment_method': 'cash'
            }
        )
        if created_p9:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Платеж: {user3.email} -> курс "{course1.title}" = 4999.00 ₽'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ⚡ Платеж уже существует: {user3.email} -> курс "{course1.title}"'))

        # ==================== 6. ИТОГИ ====================
        self.stdout.write(self.style.WARNING('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS('🎉 БАЗА ДАННЫХ УСПЕШНО ЗАПОЛНЕНА!'))
        self.stdout.write(self.style.WARNING('=' * 50))

        # Статистика
        self.stdout.write(self.style.WARNING('\n📊 СТАТИСТИКА:'))
        self.stdout.write(f'  📚 Курсов: {Course.objects.count()}')
        self.stdout.write(f'  📖 Уроков: {Lesson.objects.count()}')
        self.stdout.write(f'  👥 Пользователей: {User.objects.count()}')
        self.stdout.write(f'  💰 Платежей: {Payment.objects.count()}')

        # Информация для входа
        self.stdout.write(self.style.WARNING('\n🔐 ДАННЫЕ ДЛЯ ВХОДА:'))
        self.stdout.write('  Администратор: prokopjev.stenka@yandex.ru / admin0625')
        self.stdout.write('  Тестовые пользователи: ivan@example.com, maria@example.com, alexey@example.com / user123')

        self.stdout.write(self.style.WARNING('\n🚀 Можете запускать сервер:'))
        self.stdout.write('  python manage.py runserver')
