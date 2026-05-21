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
| PostgreSQL | 16+ | База данных |
| JWT | - | Аутентификация |
| Stripe | 15.1.0 | Платежная система |
| Celery | 5.6.3 | Асинхронные задачи |
| Redis | 7.4.0 | Брокер Celery |
| Docker | 24+ | Контейнеризация |
| Docker Compose | 2.20+ | Оркестрация |

---

## 🐳 Запуск с Docker (рекомендуемый способ)

### Предварительные требования

- Установленный [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Установленный [Docker Compose](https://docs.docker.com/compose/install/)

### Быстрый старт


*1. Клонируйте репозиторий*
```
git clone https://github.com/ваш_логин/LMS_systems.git
cd LMS_systems
```
*2. Создайте файл с переменными окружения для Docker*
```
cp .env.example .env.docker
```
*2. Отредактируйте* ```.env.docker```:

```

SECRET\_KEY=django-insecure-change-this-in-production

DB\_NAME=lms\_database

DB\_USER=postgres

DB\_PASSWORD=postgres123

DB\_HOST=db

DB\_PORT=5432

DEBUG=True

ALLOWED\_HOSTS=localhost,127.0.0.1

REDIS\_URL=redis://redis:6379

STRIPE\_PUBLISHABLE\_KEY=pk\_test\_dummy

STRIPE\_SECRET\_KEY=sk\_test\_dummy
```
**Важно:**DB_HOST=dbиREDIS_URL=redis://redis:6379— это имена сервисов в Docker Compose.


*3. Запустите все сервисы одной командой*
```
docker-compose --env-file .env.docker up -d --build
```
*4. Примените миграции*
```
docker-compose --env-file .env.docker exec web python manage.py migrate
```
*5. Создайте суперпользователя*
```
docker-compose --env-file .env.docker exec web python manage.py createsuperuser
```
### Проверка работы

| Адрес | Назначение |
| --- | --- |
| <http://localhost:8000/swagger/> | API документация (Swagger) |
| <http://localhost:8000/redoc/> | API документация (ReDoc) |
| <http://localhost:8000/admin/> | Админ-панель Django |

### Полезные команды Docker


*Просмотр статуса контейнеров*
```
docker-compose --env-file .env.docker ps
```
*Просмотр логов*
```
docker-compose --env-file .env.docker logs -f
```
*Остановка всех сервисов*
```
docker-compose --env-file .env.docker down
```
*Перезапуск конкретного сервиса*
```
docker-compose --env-file .env.docker restart web
```
*Вход в контейнер Django*
```
docker-compose --env-file .env.docker exec web bash
```
*Запуск тестов*
```
docker-compose --env-file .env.docker exec web python manage.py test
```
*Создание дампа базы данных*
```
docker-compose --env-file .env.docker exec db pg\_dump -U postgres lms\_database > backup.sql
```
### Структура сервисов

| Сервис | Описание | Порт (внешний) |
| --- | --- | --- |
| web | Django + Gunicorn | 8000 |
| db | PostgreSQL | - (только expose) |
| redis | Redis Cache/Broker | - (только expose) |
| celery | Celery Worker | - |
| celery-beat | Celery Beat Scheduler | - |

## 🚀 Локальная установка и запуск (без Docker)

### 1. Клонирование репозитория



git clone https://github.com/ваш\_логин/LMS\_systems.git

cd LMS\_systems

### 2. Создание виртуального окружения



*Windows*
```
python -m venv .venv

.venv\Scripts\activate
```
*Linux/Mac*
```
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
Отредактируйте```.env```файл, указав свои данные:
```
env
```
# Django Secret Key
```
SECRET\_KEY=django-insecure-\*\*\*СГЕНЕРИРУЙТЕ СВОЙ\*\*\*
```
# PostgreSQL Database
```
DB\_NAME=lms\_database

DB\_USER=postgres

DB\_PASSWORD=\*\*\*ВАШ ПАРОЛЬ\*\*\*

DB\_HOST=localhost

DB\_PORT=5432

# Django Settings

DEBUG=True

ALLOWED\_HOSTS=localhost,127.0.0.1

# Redis / Celery

REDIS\_URL=redis://127.0.0.1:6379

# Stripe

STRIPE\_PUBLISHABLE\_KEY=pk\_test\_\*\*\*

STRIPE\_SECRET\_KEY=sk\_test\_\*\*\*
```
### 5. Создание базы данных PostgreSQL

```

CREATE DATABASE lms\_database;
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



*Windows (через WSL)*
```
sudo service redis-server start
```
*Linux*
```
sudo systemctl start redis
```
*Или через Docker*
```
docker run -d -p 6379:6379 redis
```
### 9. Запуск Celery Worker



*Windows*
```
celery -A config worker -l info -P eventlet
```
*Linux/Mac*
```
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

## 📋 Файлы для Docker

| Файл | Назначение |
| --- | --- |
| Dockerfile | Инструкции для сборки Docker-образа Django |
| docker-compose.yml | Оркестрация 5 сервисов (db, redis, web, celery, celery-beat) |
| .dockerignore | Исключение ненужных файлов из Docker-образа |
| .env.example | Шаблон переменных окружения |

## 🔗 Ссылки

* [Django](https://www.djangoproject.com/)
* [DRF](https://www.django-rest-framework.org/)
* [Celery](https://docs.celeryq.dev/)
* [Stripe](https://stripe.com/docs/api)
* [Redis](https://redis.io/)
* [Docker](https://www.docker.com/)

**© 2026 LMS\_systems. Все права защищены.**
