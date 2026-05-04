# LMS_systems - Система управления обучением

## 📖 Описание проекта

LMS_systems — это полнофункциональная система управления обучением (Learning Management System) с REST API, разработанная на Django и Django REST Framework. Проект предоставляет возможности для управления курсами, уроками, пользователями, подписками и платежами.

### Основные возможности

- ✅ Управление курсами и уроками (CRUD)
- ✅ Кастомная модель пользователя с авторизацией по email
- ✅ JWT аутентификация
- ✅ Права доступа (модераторы, владельцы)
- ✅ Подписка на обновления курсов
- ✅ Интеграция с платежной системой Stripe
- ✅ Асинхронная обработка задач через Celery
- ✅ Периодические задачи (блокировка неактивных пользователей)
- ✅ Фильтрация, поиск и пагинация
- ✅ Валидация данных (ссылки только на YouTube)
- ✅ Документация API (Swagger/ReDoc)
- ✅ Тесты с покрытием (coverage)

---

## 🛠 Технологии

| Технология | Версия | Назначение |
|------------|--------|------------|
| Python | 3.12+ | Язык программирования |
| Django | 6.0.3 | Web-фреймворк |
| Django REST Framework | 3.17.1 | API фреймворк |
| PostgreSQL | 15+ | База данных |
| JWT | - | Аутентификация |
| Stripe | 15.1.0 | Платежная система |
| Celery | 5.6.3 | Асинхронные задачи |
| Redis | 7.4.0 | Брокер Celery |
| drf-yasg | 1.21.15 | Swagger документация |
| django-filter | 25.2 | Фильтрация |

---

## 📁 Структура проекта
```
LMS_systems/
├── config/                                 # Конфигурация проекта
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py                           # Настройки Celery
│   ├── settings.py                         # Настройки Django
│   ├── urls.py                             # Главные маршруты
│   └── wsgi.py
│
├── users/                                  # Приложение пользователей
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                           # User, Payment
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   ├── tasks.py                            # Celery задачи
│   └── migrations/
│       └── __init__.py
│
├── lms/                                    # Приложение курсов и уроков
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                           # Course, Lesson, Subscription
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── validators.py                       # Валидатор YouTube ссылок
│   ├── services.py                         # Stripe сервис
│   ├── tasks.py                            # Celery задачи
│   └── migrations/
│       └── __init__.py
│
├── media/                                  # Загружаемые пользователем файлы
├── static/                                 # Статические файлы
│
├── .env                                    # Переменные окружения (не в Git)
├── .env.example                            # Пример переменных окружения
├── .flake8                                 # Настройки линтера
├── .gitignore                              # Игнорируемые файлы Git
├── manage.py                               # Управляющий скрипт Django
├── requirements.txt                        # Зависимости проекта
├── celery.py                               # Celery приложение (корневой)
├── coverage.txt                            # Отчёт о покрытии тестами
└── README.md                               # Документация проекта
```

---

## 🚀 Установка и запуск

### 1. Клонирование репозитория

```
git clone https://github.com/ваш_логин/LMS_systems.git
cd LMS_systems
```
### 2. Создание виртуального окружения
```
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```
### 3. Установка зависимостей
```
pip install -r requirements.txt
```
### 4. Настройка переменных окружения
```
cp .env.example .env
```
Отредактируйте .env файл, указав свои данные:
```
# Django Secret Key
SECRET_KEY=django-insecure-***СГЕНЕРИРУЙТЕ СВОЙ***

# PostgreSQL Database
DB_NAME=lms_database
DB_USER=postgres
DB_PASSWORD=***ВАШ ПАРОЛЬ***
DB_HOST=localhost
DB_PORT=5432

# Django Settings
DEBUG=True
ALLOWED_HOSTS=

# Time Zone
TIME_ZONE=Europe/Moscow

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_***
STRIPE_SECRET_KEY=sk_test_***

# Redis / Celery
REDIS_URL=redis://127.0.0.1:6379
```
### 5. Создание базы данных PostgreSQL
```
CREATE DATABASE lms_database;
```
### 6. Применение миграций
```
python manage.py migrate
```
### 7. Создание суперпользователя
```
python manage.py createsuperuser
```
### 8. Запуск Redis
```
# Windows (через WSL)
sudo service redis-server start

# Linux
sudo systemctl start redis

# Или через Docker
docker run -d -p 6379:6379 redis

# Проверка
redis-cli ping  # Должен вернуть PONG
```
### 9. Запуск Celery Worker
```
# Windows
celery -A config worker -l info -P eventlet

# Linux/Mac
celery -A config worker -l info
```
### 10. Запуск Celery Beat (планировщик)
```
celery -A config beat -l info
```
### 11. Запуск Django сервера
```
python manage.py runserver
```
## 🔗 API Эндпоинты

### Аутентификация

| Method | Endpoint | Описание |
| --- | --- | --- |
| POST | /api/token/ | Получение JWT токена |
| POST | /api/token/refresh/ | Обновление JWT токена |
| POST | /api/register/ | Регистрация пользователя |

### Пользователи

| Method | Endpoint | Описание |
| --- | --- | --- |
| GET | /api/users/ | Список пользователей |
| GET | /api/users/{id}/ | Профиль пользователя |
| PUT/PATCH | /api/users/{id}/ | Обновление профиля |
| DELETE | /api/users/{id}/ | Удаление пользователя |

### Курсы

| Method | Endpoint | Описание |
| --- | --- | --- |
| GET | /api/courses/ | Список курсов (пагинация) |
| POST | /api/courses/ | Создание курса |
| GET | /api/courses/{id}/ | Детали курса |
| PUT/PATCH | /api/courses/{id}/ | Обновление курса |
| DELETE | /api/courses/{id}/ | Удаление курса |

### Уроки

| Method | Endpoint | Описание |
| --- | --- | --- |
| GET | /api/lessons/ | Список уроков |
| POST | /api/lessons/ | Создание урока |
| GET | /api/lessons/{id}/ | Детали урока |
| PUT/PATCH | /api/lessons/{id}/ | Обновление урока |
| DELETE | /api/lessons/{id}/ | Удаление урока |

### Подписки

| Method | Endpoint | Описание |
| --- | --- | --- |
| POST | /api/subscribe/ | Подписка/отписка на курс |

### Платежи (Stripe)

| Method | Endpoint | Описание |
| --- | --- | --- |
| GET | /api/payments/ | Список платежей |
| POST | /api/payments/ | Создание платежа |
| GET | /api/payments/{id}/status/ | Статус платежа |
| GET | /api/payments/test-cards/ | Список тестовых карт |

### Документация

| Method | Endpoint | Описание |
| --- | --- | --- |
| GET | /swagger/ | Swagger UI |
| GET | /redoc/ | ReDoc |
| GET | /swagger.json | Swagger JSON |
| GET | /swagger.yaml | Swagger YAML |
## 🧪 Тестирование
### Запуск всех тестов
```
python manage.py test
```
### Запуск тестов конкретного приложения
```
python manage.py test lms
python manage.py test users
```
### Покрытие тестами
```
coverage run --source='.' manage.py test
coverage report
coverage html
```
### Результат
```
Ran 40 tests in XX.XXXs
OK
Coverage: ~87%
```
## 🔧 Тестовые карты Stripe

Для тестирования оплаты используйте следующие тестовые карты:

| Карта | Номер | CVV | Срок |
| --- | --- | --- | --- |
| Visa (успех) | 4242 4242 4242 4242 | 123 | любая будущая дата |
| Mastercard (успех) | 5555 5555 5555 4444 | 123 | любая будущая дата |
| Amex (успех) | 3782 8224 6310 005 | 1234 | любая будущая дата |

## 👥 Права доступа

| Роль | Права |
| --- | --- |
| **Администратор (is\_staff)** | Полный доступ ко всему |
| **Модератор (группа moderators)** | Просмотр/редактирование любых курсов и уроков (без создания/удаления) |
| **Владелец** | Полный доступ к своим курсам и урокам |
| **Пользователь** | Просмотр своих курсов, подписка, оплата |

## 📧 Celery задачи

| Задача | Описание | Триггер |
| --- | --- | --- |
| send\_course\_update\_notification | Уведомление подписчиков об обновлении курса | Обновление курса (через 4+ часа) |
| send\_payment\_success\_email | Письмо об успешной оплате | Создание платежа |
| block\_inactive\_users | Блокировка пользователей без входа более месяца | Ежедневно в 00:00 (Celery Beat) |
## 🔗 Ссылки

* [Django](https://www.djangoproject.com/)
* [DRF](https://www.django-rest-framework.org/)
* [Celery](https://docs.celeryq.dev/)
* [Stripe](https://stripe.com/docs/api)
* [Redis](https://redis.io/)

**© 2025 LMS\_systems. Все права защищены.**