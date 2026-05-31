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

SECRET_KEY=django-insecure-change-this-in-production
DB_NAME=lms_database
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=db
DB_PORT=5432
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,158.160.87.197
REDIS_URL=redis://redis:6379
STRIPE_PUBLISHABLE_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key
TIME_ZONE=Europe/Moscow
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
docker-compose --env-file .env.docker logs web --tail=50
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
docker-compose --env-file .env.docker exec db pg_dump -U postgres lms_database > backup.sql
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
**4. ЗАПУСК ВСЕХ СЕРВИСОВ ОДНОЙ КОМАНДОЙ**

```
docker-compose --env-file .env.docker up -d --build
```
**5. Примените миграции**

```
docker-compose --env-file .env.docker exec web python manage.py migrate
```
**6. Создайте суперпользователя**

```
docker-compose --env-file .env.docker exec web python manage.py createsuperuser
```
**7. Создайте группы модераторов (опционально)**

```
docker-compose --env-file .env.docker exec web python manage.py create\_groups
```
### Проверка работы

| Адрес | Назначение |
| --- | --- |
| <http://localhost/health/> | Health check (должен вернуть "healthy") |
| [http://localhost/swagger/](http://localhost/swagger/%22%20%5Ct%20%22_blank) | API документация (Swagger) |
| <http://localhost/redoc/> | API документация (ReDoc) |
| <http://localhost/admin/> | Админ-панель Django |

### Полезные команды Docker

**Просмотр статуса контейнеров**

```
docker-compose --env-file .env.docker ps
```
**Просмотр логов**

```
docker-compose --env-file .env.docker logs -f

docker-compose --env-file .env.docker logs web --tail=50
```
**Остановка всех сервисов**

```
docker-compose --env-file .env.docker down
```
**Перезапуск конкретного сервиса**

```
docker-compose --env-file .env.docker restart web
```
**Вход в контейнер Django**

```
docker-compose --env-file .env.docker exec web bash
```
**Запуск тестов**

```
docker-compose --env-file .env.docker exec web python manage.py test
```
**Создание дампа базы данных**

```
docker-compose --env-file .env.docker exec db pg\_dump -U postgres lms\_database > backup.sql
```
## 🚀 Локальная установка и запуск (без Docker)

### 1. Клонирование репозитория

```
git clone https://github.com/ваш\_логин/LMS\_systems.git

cd LMS\_systems
```
### 2. Создание виртуального окружения

bash

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
Отредактируйте.env файл, указав свои данные.

### 5. Применение миграций

```
python manage.py migrate
```
### 6. Создание суперпользователя

```
python manage.py createsuperuser
```
### 7. Запуск Redis


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
### 8. Запуск Celery Worker


*Windows*
```
celery -A config worker -l info -P eventlet
```
*Linux/Mac*
```
celery -A config worker -l info
```
### 9. Запуск Celery Beat (планировщик)

```
celery -A config beat -l info
```
### 10. Запуск Django сервера

```
python manage.py runserver
```
## 🔄 CI/CD Pipeline (GitHub Actions)

### Автоматический деплой

Проект настроен на **автоматический деплой** при push в ветку main.

### Этапы CI/CD

| Этап | Описание |
| --- | --- |
| **Lint** | Проверка кода flake8 |
| **Test** | Запуск тестов Django с PostgreSQL в CI |
| **Build & Deploy** | Сборка Docker образа и деплой на сервер |

### Необходимые Secrets в GitHub

| Secret | Описание |
| --- | --- |
| SERVER\_IP | IP адрес сервера (158.160.87.197) |
| SSH\_USER | Имя пользователя для SSH (aibolit\_aurus) |
| SSH\_PRIVATE\_KEY | Приватный SSH ключ |

### Статус деплоя

* Следите за статусом:[https://github.com/ваш\_логин/LMS\_systems/actions](https://github.com/%D0%B2%D0%B0%D1%88_%D0%BB%D0%BE%D0%B3%D0%B8%D0%BD/LMS_systems/actions)
* Зеленый ✅ — успешный деплой
* Красный ❌ — ошибка (смотрите логи)

### Проверка после деплоя

После успешного деплоя сервер доступен по адресу:

* **Health check**:<http://158.160.87.197/health/>→ должно вернуть healthy
* **Swagger документация**:<http://158.160.87.197/swagger/>
* **ReDoc документация**:<http://158.160.87.197/redoc/>

## 🌍 Деплой на сервер (Yandex Cloud)

### Информация о сервере

| Параметр | Значение |
| --- | --- |
| IP адрес | 158.160.87.197 |
| Пользователь | aibolit\_aurus |
| ОС | Ubuntu 24.04 LTS |
| CPU | 2 vCPU |
| RAM | 2 ГБ |
| Диск | 10 ГБ |

### Настройка сервера (выполняется один раз)


*Подключение к серверу*
```
ssh -l aibolit_aurus 158.160.87.197
```
*Установка Docker*
```
sudo apt update
```
```
sudo apt install -y docker.io docker-compose-plugin
```
```
sudo systemctl start docker
```
```
sudo usermod -aG docker $USER
```
*Выход и повторный вход*
```
exit
```
```
ssh -l aibolit\_aurus 158.160.87.197
```
*Создание директории проекта*
```
mkdir -p ~/LMS\_systems

cd ~/LMS\_systems
```
*Создание .env.docker*
```
cat > .env.docker << 'EOF'
```
```
SECRET\_KEY=django-insecure-temp-key-for-docker-only

DB\_NAME=lms\_database

DB\_USER=postgres

DB\_PASSWORD=temp123

DB\_HOST=db

DB\_PORT=5432

DEBUG=False

ALLOWED\_HOSTS=158.160.87.197,localhost,127.0.0.1

REDIS\_URL=redis://redis:6379

STRIPE\_PUBLISHABLE\_KEY=pk\_test\_dummy

STRIPE\_SECRET\_KEY=sk\_test\_dummy

TIME\_ZONE=Europe/Moscow
```
EOF

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
```
```
coverage report
```
```
coverage html
```
### Результат

text

Ran 40 tests in XX.XXXs

OK

Coverage: ~87%

## 🔧 Тестовые карты Stripe

Для тестирования оплаты используйте следующие тестовые карты:

| Карта | Номер | CVV | Срок |
| --- | --- | --- | --- |
| Visa (успех) | 4242 4242 4242 4242 | 123 | любая будущая дата |
| Mastercard (успех) | 5555 5555 5555 4444 | 123 | любая будущая дата |
| Amex (успех) | 3782 8224 6310 005 | 1234 | любая будущая дата |
| Discover (успех) | 6011 1111 1111 1117 | 123 | любая будущая дата |

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
| docker-compose.yml | Оркестрация 6 сервисов (nginx, db, redis, web, celery, celery-beat) |
| nginx/default.conf | Конфигурация Nginx reverse proxy |
| .dockerignore | Исключение ненужных файлов из Docker-образа |
| .env.docker.example | Шаблон переменных окружения для Docker |
| .env.example | Шаблон переменных окружения для локальной разработки |

## 📁 Структура проекта

```
LMS\_systems/

├── .github/workflows/

│ └── deploy.yml # CI/CD pipeline

├── config/

│ ├── settings.py # Настройки Django

│ ├── urls.py # URL маршруты (включая /health/)

│ └── celery.py # Конфигурация Celery

├── lms/ # Приложение курсов и уроков

├── users/ # Приложение пользователей и платежей

├── nginx/

│ └── default.conf # Конфигурация Nginx

├── Dockerfile

├── docker-compose.yml

├── .env.docker.example

├── .env.example

├── .dockerignore

├── requirements.txt

└── README.md
```
## 🔗 Ссылки

* [Django](https://www.djangoproject.com/)
* [DRF](https://www.django-rest-framework.org/)
* [Celery](https://docs.celeryq.dev/)
* [Stripe](https://stripe.com/docs/api)
* [Redis](https://redis.io/)
* [Docker](https://www.docker.com/)
* [GitHub Actions](https://github.com/features/actions)
* [Yandex Cloud](https://cloud.yandex.ru/)

## 📝 Примечания

1. **Для тестирования оплаты** используйте тестовые карты Stripe
2. **Не забудьте остановить ВМ** в Yandex Cloud
3. **Перед деплоем убедитесь**, что DEBUG=False в .env.docker
4. **Health check** доступен по адресу /health/ для мониторинга

**© 2026 LMS\_systems. Все права защищены.**
